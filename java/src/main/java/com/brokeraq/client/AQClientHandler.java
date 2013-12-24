package com.brokeraq.client;

import com.brokeraq.client.model.OrderDirectory;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.logging.Logger;

import org.jboss.netty.channel.ChannelEvent;
import org.jboss.netty.channel.ChannelHandlerContext;
import org.jboss.netty.channel.ChannelStateEvent;
import org.jboss.netty.channel.ExceptionEvent;
import org.jboss.netty.channel.MessageEvent;
import org.jboss.netty.channel.SimpleChannelUpstreamHandler;

import com.activequant.domainmodel.TimeStamp;
import com.activequant.domainmodel.trade.event.OrderAcceptedEvent;
import com.activequant.domainmodel.trade.event.OrderCancelledEvent;
import com.activequant.domainmodel.trade.event.OrderEvent;
import com.activequant.domainmodel.trade.event.OrderFillEvent;
import com.activequant.domainmodel.trade.event.OrderPendingEvent;
import com.activequant.domainmodel.trade.event.OrderRejectedEvent;
import com.activequant.domainmodel.trade.event.OrderReplacedEvent;
import com.activequant.domainmodel.trade.order.LimitOrder;
import com.activequant.domainmodel.trade.order.MarketOrder;
import com.activequant.domainmodel.trade.order.Order;
import com.activequant.domainmodel.trade.order.OrderSide;
import com.activequant.domainmodel.trade.order.SingleLegOrder;
import com.activequant.domainmodel.trade.order.StopOrder;
import com.activequant.messages.AQMessages;
import com.activequant.messages.AQMessages.LoginResponse;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;
import java.util.logging.Level;

/**
 * The AQClientHandler is used in the Client Pipeline of Netty for processing
 * incoming messages. Do not use directly, but stick to the BlackBoxImpl.
 *
 * @author ustaudinger
 */
class AQClientHandler extends SimpleChannelUpstreamHandler {

    private static final Logger logger = Logger.getLogger(AQClientHandler.class
            .getName());
    private final BlackBoxImpl b = (BlackBoxImpl) BlackBoxImpl.instance();
    private SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd-HH:mm:ss.SSS");
    private OrderDirectory orderDirectory = OrderDirectory.instance();
    // we'll use the seenExecIds to keep drop execution IDs.  
    private Set<String> seenExecIds = new HashSet<String>();

    @Override
    public void handleUpstream(ChannelHandlerContext ctx, ChannelEvent e)
            throws Exception {
        if (e instanceof ChannelStateEvent) {
            logger.info(e.toString());
        }
        super.handleUpstream(ctx, e);
    }

    /**
     * this method processes all incoming messages.
     */
    @Override
    public void messageReceived(ChannelHandlerContext ctx, MessageEvent e) {
        AQMessages.BaseMessage bm = (AQMessages.BaseMessage) e.getMessage();
        System.out.println(bm);
        logger.info(bm.toString());
        // let's process this message.
        if (bm.hasExtension(AQMessages.LoginResponse.cmd)) {
            LoginResponse lr = bm.getExtension(AQMessages.LoginResponse.cmd);
            if (lr.getStatus().startsWith("Welcome.")) {
                logger.info("Signalling read to black box. ");
                b.getReadyEvent().fire("Logged in.");
            } else {
                b.getDisconnectedEvent().fire(lr.getStatus());
            }
        } else {
            // ok, it's not a login response, so let's delegate it onwards
            // to our black box impl.
            if (bm.hasExtension(AQMessages.ServerTime.cmd)) {
                System.out.println("********* SERVER TIME");
                b.getServerTimeEvent().fire(
                        bm.getExtension(AQMessages.ServerTime.cmd));
            } else if (bm.hasExtension(AQMessages.AccountDataMessage.cmd)) {
                AQMessages.AccountDataMessage a = bm
                        .getExtension(AQMessages.AccountDataMessage.cmd);
                b.getAccountEvent().fire(a);
            } else if (bm.hasExtension(AQMessages.ExecutionReport.cmd)) {
                // let's process it further.
                onMessage((AQMessages.ExecutionReport) bm
                        .getExtension(AQMessages.ExecutionReport.cmd));
            } else if (bm.hasExtension(AQMessages.PositionReport.cmd)) {
                AQMessages.PositionReport a = bm
                        .getExtension(AQMessages.PositionReport.cmd);
                b.getRawPositionEvent().fire(a);
            } else if (bm.hasExtension(AQMessages.MarketDataSnapshot.cmd)) {
                // let's process it further.
                onMessage((AQMessages.MarketDataSnapshot) bm
                        .getExtension(AQMessages.MarketDataSnapshot.cmd));
            } else if (bm.hasExtension(AQMessages.OHLC.cmd)) {
                // let's process it further.
                onMessage((AQMessages.OHLC) bm
                        .getExtension(AQMessages.OHLC.cmd));
            }
        }
    }

    /**
     * This method receives all execution reports and it will drop duplicate
     * execution reports.
     *
     * @param execReport
     */
    private void onMessage(AQMessages.ExecutionReport execReport) {
        OrderEvent oe = null;
        int orderStatus = execReport.getOrdStatus();
        String clientOrderId = null;
        String inst = execReport.getTradInstId();

        boolean restated = false;

        clientOrderId = execReport.getClOrdId();
        String execId = execReport.getExecId();
        // let's check if we have seen this execution ID already. If, then we'll drop it.
        if (seenExecIds.contains(execId)) {
            return;
        }
        // ok, still here, means we haven't seen this execution id, yet. 
        seenExecIds.add(execId);
        // ok, unseen execution report, let's continue. 
        String acmOrderId = execReport.getOrderId();

        OrderSide side = null;

        switch (orderStatus) {
            case 8:
                // OrdStatus.REJECTED
                oe = new OrderRejectedEvent();
                if (execReport.getText() != null) {
                    String reason = execReport.getText();
                    ((OrderRejectedEvent) oe).setReason(reason);
                }
                break;
            case 0:
                // OrdStatus.NEW
                logger.log(Level.INFO, "New order status in exec report {0} found. ", execId);
                if (acmOrderId.equals("0")) {
                    // accepted, but no ID assigned yet. 
                    oe = new OrderPendingEvent();
                } else {
                    // ok, the order got accepted by ACM and it is now working. 
                    oe = new OrderAcceptedEvent();
                    // have to check if it is a response to a mass status request.                    
                }
                // 
                if (execReport.getMassStatusReqId() == null) {
                    // ok, no mass request id found.
                } else {
                    // ok, we have received a response to a mass status request. 
                    // A mass status request results from a user login or from the server 
                    // requesting current data snapshots. 
                    // 
                    // have to check if this a response to an update event.
                    if (clientOrderId.startsWith("PDT:")) {
                        // ok, seems to be an update, that update has been accepted? 
                    } else {
                        oe.setRefOrderId(clientOrderId);
                    }
                }
                break;
            case 4:
                // OrdStatus.CANCELED
                oe = new OrderCancelledEvent();
                break;
            case 2:
                // OrdStatus.FILLED
                OrderFillEvent ofe = new OrderFillEvent();
                ofe.setExecId(execReport.getExecId());
                String tt = execReport.getTransactTime();
                try {
                    ofe.setTimeStamp(new TimeStamp(sdf.parse(tt)));
                } catch (ParseException e) {
                    return;
                }
                double leftQuantity = execReport.getLeavesQty();
                ofe.setLeftQuantity(leftQuantity);

                ofe.setFillPrice(execReport.getAvgPx());
                ofe.setFillAmount(execReport.getCumQty());
                ofe.setLeftQuantity(execReport.getLeavesQty());

                side = execReport.getSide() == 1 ? OrderSide.BUY : OrderSide.SELL;
                logger.log(Level.INFO, "Side {0} resulted in {1}", new Object[]{execReport.getSide(), side.name()});
                ofe.setSide(side);

                ofe.setOptionalInstId(inst);

                // ok, let's delegate the event further.
                oe = ofe;

                break;
            default:
                break;
        }


        // ok, we have properly built the order event. 
        if (oe != null) {
            // 
            if (clientOrderId != null) {
                // check if we have some cancellations or updates ...
                String entireOrderId = clientOrderId;
                String cmd = "";
                if (clientOrderId.indexOf(":") != -1) {
                    String[] s = clientOrderId.split(":");
                    clientOrderId = s[1];
                    cmd = s[0];
                }

                // check if we had an order update event.
                // if this order update event has been rejected, then let's go.
                if (execReport.getOrdStatus() == 8) {
                    // OrdStatus.REJECTED
                    if (!entireOrderId.startsWith("ID")) {
                        // we then want to signal that JUST THE UPDATE OR THE
                        // CANCELLATION got rejected.
                        clientOrderId = entireOrderId;
                    }
                }
                // set the ref order id.
                oe.setRefOrderId(clientOrderId);
                // let's look up our ref order and let's see if we have this order already. 
                Order refOrder = orderDirectory.getOrder(clientOrderId);
                if (refOrder == null) {
                    refOrder = restoreOrderTracker(execReport);
                    orderDirectory.addOrder(refOrder);
                    oe.setOptionalInstId(((SingleLegOrder) refOrder).getTradInstId());
                    // ok, i also have to set the reference order ...
                } else {
                    logger.info("AQClientHandler found the order in its order directory.");
                }


                // 
                oe.setRefOrder(refOrder);
                // we'll also set the optional instrument id .. 
                oe.setOptionalInstId(inst);
                // TODO: in case of an order fill event, we should also update the 
                // reference order with the filled quantities. 
            }
            b.getOrderEvent().fire(oe);
        } else {
            logger.info("No order event found. ");
        }
    }

    public SingleLegOrder restoreOrderTracker(AQMessages.ExecutionReport er) {
        logger.log(Level.INFO, "Restoring order tracker. ");
        String orderId = er.getClOrdId();
        String orderType = er.getOrdType();
        logger.log(Level.INFO, "Order tracker order type: {0}", orderType);
        //
        if (orderType.equals("1")) {
            //
            MarketOrder lo = new MarketOrder();
            lo.setOrderId(orderId);
            // 
            lo.setQuantity(er.getOrderQty());
            lo.setOpenQuantity(lo.getQuantity() - er.getCumQty());
            lo.setOrderSide(er.getSide() == 1 ? OrderSide.BUY
                    : OrderSide.SELL);
            lo.setTradInstId(er.getTradInstId());
            // ok, market order reconstructed. 
            return lo;
        } else if (orderType.equals("2")) {
            //
            LimitOrder lo = new LimitOrder();
            lo.setOrderId(orderId);
            // 
            lo.setLimitPrice(er.getPrice());
            lo.setQuantity(er.getOrderQty());
            lo.setOpenQuantity(lo.getQuantity() - er.getCumQty());
            lo.setOrderSide(er.getSide() == 1 ? OrderSide.BUY
                    : OrderSide.SELL);
            logger.log(Level.INFO, "Side {0} resulted in {1}", new Object[]{er.getSide(), lo.getOrderSide()});
            lo.setTradInstId(er.getTradInstId());
            // ok, limit order done. 
            return lo;
        } else if (orderType.equals("3")) {
            // STOP ORDER
            StopOrder lo = new StopOrder();
            lo.setOrderId(orderId);
            lo.setStopPrice(er.getPrice());
            lo.setQuantity(er.getOrderQty());
            lo.setOpenQuantity(lo.getQuantity() - er.getCumQty());
            lo.setOrderSide(er.getSide() == 1 ? OrderSide.BUY
                    : OrderSide.SELL);
            lo.setTradInstId(er.getTradInstId());
            // done.
            return lo;
        }

        return null;
    }

    @Override
    public void channelConnected(ChannelHandlerContext ctx, ChannelStateEvent e)
            throws Exception {
        logger.info("Channel connected.");
        super.channelConnected(ctx, e);

        //
        b.getConnectedEvent().fire("Connection established");
    }

    @Override
    public void channelClosed(ChannelHandlerContext ctx, ChannelStateEvent e)
            throws Exception {
        logger.info("Channel closed.");
        super.channelDisconnected(ctx, e);

        b.getDisconnectedEvent().fire("Channel closed");
    }

    @Override
    public void channelDisconnected(ChannelHandlerContext ctx,
            ChannelStateEvent e) throws Exception {
        logger.info("Channel disconnected.");
        super.channelDisconnected(ctx, e);
        b.getDisconnectedEvent().fire("Channel disconnected");
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, ExceptionEvent e) {
        logger.log(Level.WARNING, "Exception caught {0}", e.getCause());
        logger.throwing(this.getClass().getName(), "exception Caught", e.getCause());
        e.getChannel().close();
    }

    private void onMessage(AQMessages.MarketDataSnapshot marketDataSnapshot) {
        b.getMdsEvent().fire(marketDataSnapshot);
    }

    private void onMessage(AQMessages.OHLC ohlc) {
        b.getOhlcEvent().fire(ohlc);
    }
}
