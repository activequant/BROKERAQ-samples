package com.brokeraq.client;

import com.brokeraq.client.model.OrderDirectory;
import com.activequant.domainmodel.TimeFrame;
import com.activequant.domainmodel.TimeStamp;
import com.activequant.domainmodel.trade.event.OrderAcceptedEvent;
import com.activequant.domainmodel.trade.event.OrderCancelSubmittedEvent;
import com.activequant.domainmodel.trade.event.OrderCancelledEvent;

import java.util.Map;
import java.util.logging.Logger;

import com.activequant.domainmodel.trade.event.OrderEvent;
import com.activequant.domainmodel.trade.event.OrderFillEvent;
import com.activequant.domainmodel.trade.event.OrderRejectedEvent;
import com.activequant.domainmodel.trade.event.OrderReplacedEvent;
import com.activequant.domainmodel.trade.event.OrderSubmittedEvent;
import com.activequant.domainmodel.trade.event.OrderUpdateSubmittedEvent;
import com.activequant.domainmodel.trade.order.LimitOrder;
import com.activequant.domainmodel.trade.order.MarketOrder;
import com.activequant.domainmodel.trade.order.Order;
import com.activequant.domainmodel.trade.order.OrderSide;
import com.activequant.domainmodel.trade.order.SingleLegOrder;
import com.activequant.domainmodel.trade.order.StopOrder;
import com.activequant.interfaces.blackbox.IBlackBox;
import com.activequant.interfaces.utils.IEventListener;
import com.activequant.interfaces.utils.IEventSource;
import com.activequant.messages.AQMessages;
import com.activequant.messages.AQMessages.AccountDataMessage;
import com.activequant.messages.AQMessages.BaseMessage;
import com.activequant.messages.AQMessages.MDSubscribeResponse;
import com.activequant.messages.AQMessages.MarketDataSnapshot;
import com.activequant.messages.AQMessages.OHLC;
import com.activequant.messages.AQMessages.PositionReport;
import com.activequant.messages.AQMessages.ServerTime;
import com.activequant.messages.AQMessages.Tick;
import com.activequant.utils.UniqueTimeStampGenerator;
import com.activequant.utils.events.Event;
import com.brokeraq.client.exceptions.ConnectionAttemptInProgress;
import com.brokeraq.client.exceptions.NoUsernamePassword;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;

/**
 * The black box constitutes the preferred way to communicate with the trading
 * servers.
 * <p>It is an event based interface to the trading infrastructure and provides
 * convenience methods to connect and disconnect from the infrastructure. Upon
 * disconnect, it tries to reconnect in five second intervals until it succeeds
 * or gets stopped.</p>
 *
 * <p>All implementations must code against the stream black box.</p>
 *
 * @author ustaudinger
 *
 */
public class BlackBoxImpl implements IBlackBox {

    private final Event<ServerTime> serverTimeEvent = new Event<ServerTime>();
    private final Event<String> connectedEvent = new Event<String>();
    private final Event<String> disconnectedEvent = new Event<String>();
    private final Event<String> readyEvent = new Event<String>();
    private final Event<AccountDataMessage> accountDataEvent = new Event<AccountDataMessage>();
    private final Event<BaseMessage> outgoingEvent = new Event<BaseMessage>();
    private final Event<PositionReport> positionEvent = new Event<PositionReport>();
    private final Event<PositionReport> rawPositionEvent = new Event<PositionReport>();
    private final Event<OrderEvent> orderEvent = new Event<OrderEvent>();
    private final Event<OHLC> ohlcEvent = new Event<OHLC>();
    private final Event<MarketDataSnapshot> mdsEvent = new Event<MarketDataSnapshot>();
    private final Map<String, PositionReport> positionReports = new ConcurrentHashMap<String, PositionReport>();
    private final List<Subscription> subscriptions = new ArrayList<Subscription>();
    private String password;
    private String userName;
    private MessageFactory mf = new MessageFactory();
    private static BlackBoxImpl instance = null;
    private static Object lock = new Object();
    private static final Logger log = Logger.getLogger(BlackBoxImpl.class
            .getName());
    private boolean reconnectInProgress = false;
    private Thread reconnector = null;
    private final Map<String, String> accountValues = new ConcurrentHashMap<String, String>();
    private final Map<String, MarketDataSnapshot> currentPrices = new ConcurrentHashMap<String, MarketDataSnapshot>();
    private Map<String, OrderEvent> orderEvents = new HashMap<String, OrderEvent>();
    private final UniqueTimeStampGenerator utsg = UniqueTimeStampGenerator.getInstance();
    // we'll also use a central order directory instance. 
    private OrderDirectory orderDirectory = OrderDirectory.instance();
    // will keep a list of order commands per order, order commands are cancellations and order updates, etc. 
    private Map<String, Object> submittedCancellations = new HashMap<String, Object>();
    private Map<String, Object> submittedOrderUpdates = new HashMap<String, Object>();
    private Map<String, Object> enqueuedOrderUpdates = new HashMap<String, Object>();

    private BlackBoxImpl() {
        mdsEvent.addEventListener(new IEventListener<MarketDataSnapshot>() {
            @Override
            public void eventFired(MarketDataSnapshot t) {
                currentPrices.put(t.getMdiId(), t);
            }
        });
        connectedEvent.addEventListener(new IEventListener<String>() {
            @Override
            public void eventFired(String arg0) {
                log.info("Black box connected.");
                // we'll reset the portfolio as we'll get the latest portfolio from the server upon reconnect. 
                positionReports.clear();
                //
                BaseMessage bm = mf.buildLogin(userName, password, "TRADE");
                send(bm);
            }
        });

        readyEvent.addEventListener(new IEventListener<String>() {
            @Override
            public void eventFired(String arg0) {
                log.info("Login succeeded, black box is ready.");
                stopReconnectThread();
                // resubscribe market data ..
                resubscribeMarketData();
            }
        });

        disconnectedEvent.addEventListener(new IEventListener<String>() {
            @Override
            public void eventFired(String arg0) {
                log.info("Black box disconnected. Will reconnected.");
                //
                if (!reconnectInProgress) {
                    spawnReconnectThread();
                }
            }
        });

        accountDataEvent.addEventListener(new IEventListener<AQMessages.AccountDataMessage>() {
            @Override
            public void eventFired(AQMessages.AccountDataMessage arg0) {
                accountValues.put(arg0.getType(), arg0.getValue());
            }
        });
        rawPositionEvent.addEventListener(new IEventListener<AQMessages.PositionReport>() {
            @Override
            public void eventFired(AQMessages.PositionReport t) {
                String key = t.getTradInstId();
                // now that we have the position report object, let's update the portfolio and 
                // let's also update the event that we send further. 
                // As we register on the event in our constructor, we can be sure to be the first one that receives this event. 
                if (positionReports.get(key) != null) {
                    AQMessages.PositionReport report = positionReports.get(key);
                    Double px = report.getEntryPrice();
                    Double q = report.getQuantity();
                    // let's update it.                     
                    q += t.getQuantity();
                    // let's also update the price ... 

                    if (Math.abs(q) > Math.abs(report.getQuantity()) && q != 0.0) {
                        px = (report.getQuantity() * report.getEntryPrice()
                                + t.getEntryPrice() * t.getQuantity()) / q;
                    }

                    BaseMessage bm = mf.buildPositionReport(key, "20130101",
                            px, q);
                    PositionReport p = bm.getExtension(AQMessages.PositionReport.cmd);
                    positionReports.put(key, p);
                } else {
                    positionReports.put(key, t);
                }
                // let's also make sure we subscribe to market prices for this instrument.                 
                subscribe(key, TimeFrame.EOD.RAW, 1);
                // ok, now that we have updated our position, let's fire the final event into the final position event. 
                positionEvent.fire(positionReports.get(key));

            }
        });


        orderEvent.addEventListener(new IEventListener<OrderEvent>() {
            @Override
            public void eventFired(OrderEvent msg) {

                log.log(Level.INFO, "Received an order event {0}", msg.toString());
                // we'll track this order event if it is an order accepted event. 
                if (msg instanceof OrderAcceptedEvent) {
                    orderEvents.put(msg.getRefOrderId(), msg);
                } else if (msg instanceof OrderRejectedEvent) {
                    orderEvents.remove(msg.getRefOrderId());
                } else if (msg instanceof OrderUpdateSubmittedEvent) {
                } else if (msg instanceof OrderReplacedEvent) {
                    submittedOrderUpdates.remove(msg.getRefOrderId());
                    // check if there is another order update pending ... 
                } else if (msg instanceof OrderCancelledEvent) {
                    orderEvents.remove(msg.getRefOrderId());
                    submittedCancellations.remove(msg.getRefOrderId());
                    // check if the user submitted order updates since 
                    // he requested a cancellation (could happen)
                } else if (msg instanceof OrderFillEvent) {
                    OrderFillEvent ofe = (OrderFillEvent) msg;
                    String instId = ofe.getOptionalInstId();
                    OrderSide side = ofe.getSide();
                    Double fillAmount = ofe.getFillAmount() * side.getSide();
                    log.log(Level.INFO, "Fill amount in order fill event: {0}", fillAmount);
                    // let's construct a new position report ... 
                    BaseMessage bm = mf.buildPositionReport(instId, ofe.getTimeStamp().getCalendar().getTime().toString(), ofe.getFillPrice(), fillAmount);
                    PositionReport p = bm.getExtension(AQMessages.PositionReport.cmd);
                    // let's propagate this position event. 
                    rawPositionEvent.fire(p);
                }
            }
        });

    }

    private void spawnReconnectThread() {
        reconnectInProgress = true;
        reconnector = new Thread(new ReconnectRunnable());
        reconnector.start();
    }

    private void stopReconnectThread() {
        reconnectInProgress = false;
    }

    public MarketDataSnapshot getQuote(String instrument) {
        MarketDataSnapshot mds = currentPrices.get(instrument);
        if (mds == null) {
            // ok, let's fetch it from our webservice. 
            try {
                URL url = new URL("http://78.47.96.150:55115/instsnap?instrument=" + instrument);
                URLConnection getConn = url.openConnection();
                getConn.connect();
                BufferedReader dis = new BufferedReader(
                        new InputStreamReader(
                        getConn.getInputStream()));
                dis.readLine();
                String l = dis.readLine();
                String[] parts = l.split(";");
                mds = mf.buildMds(instrument, Double.parseDouble(parts[3]),
                        Double.parseDouble(parts[4]), Double.parseDouble(parts[2]), Double.parseDouble(parts[5])).getExtension(MarketDataSnapshot.cmd);
                System.out.println("******** " + l);
            } catch (Exception ex) {
                ex.printStackTrace();
            }
        }
        return mds;
    }

    public Iterable<OrderEvent> getOrderEvents() {
        return orderEvents.values();
    }

    private class ReconnectRunnable implements Runnable {

        public void run() {
            while (reconnectInProgress) {
                try {
                    Thread.sleep(5000);
                    if (reconnectInProgress) {
                        connect();
                    } else {
                        // silently let it be.
                    }
                } catch (InterruptedException ex) {
                    // we don't care about the interrupted exception.
                    log.warning("Sleep got interrupted. " + ex);
                } catch (ConnectionAttemptInProgress e) {
                    log.warning("There seems to be another connection attempt in progress.");
                } catch (NoUsernamePassword e) {
                    // TODO Auto-generated catch block
                    log.warning("No username and password in black box.");
                }
            }
        }
    }

    public void setUsername(String userName) {
        this.userName = userName;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public static BlackBoxImpl instance() {
        synchronized (lock) {
            if (instance == null) {
                instance = new BlackBoxImpl();
            }
        }
        return instance;
    }

    public void connect() throws ConnectionAttemptInProgress,
            NoUsernamePassword {
        if (userName == null || password == null) {
            throw new NoUsernamePassword();
        }
        AQSocket.instance().start();
    }

    public void disconnect() {
        AQSocket.instance().stop();
    }

    @Override
    public IEventSource<AccountDataMessage> accountDataEvent() {
        return accountDataEvent;
    }

    @Override
    public IEventSource<OHLC> ohlcEvent() {
        return ohlcEvent;
    }

    @Override
    public IEventSource<OrderEvent> orderEvents() {
        return orderEvent;
    }

    /**
     * The position event carries all position reports as they are received from
     * the server to all event listeners. Position reports include actual
     * positions and supersede formerly received values.
     *
     * @return
     */
    @Override
    public IEventSource<PositionReport> positionEvent() {
        return positionEvent;
    }

    /**
     * The quote event carries all market data snapshots to event listeners. The
     * black box does not implement a subscriber pattern with a fine grained
     * distribution mechanism, but instead delivers all market data snapshots to
     * all event listeners. The API user should implement his own distribution
     * mechanism.
     *
     * @return
     */
    @Override
    public IEventSource<MarketDataSnapshot> quoteEvent() {
        return mdsEvent;
    }

    /**
     * The send message propagates a base message to the underlying socket
     * implementation.
     *
     * @param bm
     */
    @Override
    public void send(BaseMessage bm) {
        // have to be a bit smarter in here, as I need to translate messages to order trackers, etc.
        this.outgoingEvent.fire(bm);
    }

    /**
     * The server sends in regular intervals server time events. These events
     * are used by the black box to monitor the connection state.
     * Implementations may use this event to synchronize their clocks.
     *
     * @return
     */
    @Override
    public IEventSource<ServerTime> serverTimeEvent() {
        return serverTimeEvent;
    }

    @Override
    public IEventSource<MDSubscribeResponse> subscriptionResponseEvent() {
        // TODO Auto-generated method stub
        return null;
    }

    /**
     * The tick event carries tick data to subscribed consumers. The black box
     * uses the tick event to forward all received ticks to event listeners.
     * There is no subscription mechanism and no market data subscriber pattern
     * on purpose to keep the implementation simple. The API users should
     * implement their own tick event distribution mechanism in their software
     * architecture.
     *
     * @see BlackBoxImpl.quoteEvent
     *
     * @return
     */
    @Override
    public IEventSource<Tick> tickEvent() {
        // TODO Auto-generated method stub
        return null;
    }

    /**
     * The connected event is used to signal that the black box has made a
     * successful TCP connection to the server, but not that it is ready for
     * service.
     *
     * @return
     */
    @Override
    public IEventSource<String> connected() {
        return connectedEvent;
    }

    /**
     * The disconnected event signals that the black box has been disconnected.
     *
     * The disconnected event carries a string that *may* indicate the
     * disconnect reason. API users should refrain from sending messages after a
     * disconnected event has been received.
     *
     * @return
     */
    @Override
    public IEventSource<String> disconnected() {
        return disconnectedEvent;
    }

    /**
     * The ready event is fired once the black box has successfully logged in
     * and has received the login confirmation message.
     *
     * API users should subscribe to the ready event to know when the black box
     * is ready. All messages sent before the black box is ready might or might
     * not arrive at the server.
     *
     * @return
     */
    @Override
    public IEventSource<String> ready() {
        return readyEvent;
    }

    /**
     * visibility on package level intentionally
     *
     * @return
     */
    Event<String> getConnectedEvent() {
        return connectedEvent;
    }

    /**
     * visibility on package level intentionally
     *
     * @return
     */
    Event<String> getDisconnectedEvent() {
        return disconnectedEvent;
    }

    /**
     * visibility on package level intentionally
     *
     * @return
     */
    Event<MarketDataSnapshot> getMdsEvent() {
        return mdsEvent;
    }

    /**
     * visibility on package level intentionally
     *
     * @return
     */
    Event<String> getReadyEvent() {
        return readyEvent;
    }

    /**
     * visibility on package level intentionally
     *
     * @return
     */
    Event<ServerTime> getServerTimeEvent() {
        return serverTimeEvent;
    }

    /**
     * visibility on package level intentionally
     *
     * @return
     */
    Event<BaseMessage> getOutgoingMessageEvent() {
        return outgoingEvent;
    }

    /**
     * package protected method.
     *
     * @return
     */
    Event<AccountDataMessage> getAccountEvent() {
        return accountDataEvent;
    }

    Event<OrderEvent> getOrderEvent() {
        return orderEvent;
    }

    Event<PositionReport> getPositionEvent() {
        return positionEvent;
    }

    Event<PositionReport> getRawPositionEvent() {
        return rawPositionEvent;
    }

    Event<OHLC> getOhlcEvent() {
        return ohlcEvent;
    }

    /**
     * The black box keeps a copy of all account values for later reuse. The
     * black box subscribes to the account data event and updates the internal
     * account values map, thus keeping track of the account state. Examples of
     * account values are CASH, OPEN PNL, etc.
     *
     * @return
     */
    public Map<String, String> getAccountValues() {
        return accountValues;
    }

    public Map<String, PositionReport> getPositionReports() {
        return positionReports;
    }

    private boolean subscribed(Subscription s) {
        for (Subscription sub : subscriptions) {
            if (sub.instrument.equals(s.instrument) && sub.depth == s.depth && sub.tf.equals(s.tf)) {
                return true;
            }
        }
        return false;
    }

    private String format(String inst) {
        if (inst.indexOf("/") != -1) {
            return inst.replaceAll("/", "");
        }
        return inst;
    }

    public void subscribe(final String instrument, final TimeFrame timeFrame, final int depth) {
        String formattedInst = format(instrument);
        Subscription s = new Subscription(formattedInst, timeFrame, depth);
        if (!subscribed(s)) {
            log.log(Level.INFO, "Subscribing to {0} ", instrument);
            subscriptions.add(s);
            send(mf.subscribe(formattedInst, timeFrame, 1));
        }
    }

    public void unsubscribe(String instrument, TimeFrame timeFrame, int depth) {
        Subscription s = new Subscription(instrument, timeFrame, depth);
        int idx = -1;
        for (int i = 0; i < subscriptions.size(); i++) {
            if (subscriptions.get(i).instrument.equals(instrument)
                    && subscriptions.get(i).tf.equals(timeFrame)
                    && subscriptions.get(i).depth == depth) {
                idx = i;
            }
        }
        if (idx != -1) {
            subscriptions.remove(idx);
        }
        // let's send out the unsubscribe message ... 
        send(mf.unsubscribe(instrument, timeFrame));
    }

    /**
     *
     */
    private void resubscribeMarketData() {
        log.info("Resubscribing market data.");
        for (Subscription s : subscriptions) {
            send(mf.subscribe(s.instrument, s.tf, 1));
        }
    }

    class Subscription {

        final String instrument;
        final TimeFrame tf;
        final int depth;

        public Subscription(String instrument, TimeFrame tf, int depth) {
            this.instrument = instrument;
            this.tf = tf;
            this.depth = depth;
        }
    }

    /**
     *
     * @param instrument
     * @param quantity signed quantity to be ordered
     * @return the internal order id.
     */
    public String sendMarketOrder(String instrument, Double quantity) {
        // 
        String orderId = "ID" + utsg.now().getNanoseconds();

        // we'll also construct a stop order. 
        MarketOrder marketOrder = new MarketOrder();
        marketOrder.setOrderId(orderId);
        marketOrder.setTradInstId(instrument);
        marketOrder.setQuantity(quantity);
        marketOrder.setOpenQuantity(quantity);
        if (Math.signum(quantity) == 1) {
            marketOrder.setOrderSide(OrderSide.BUY);
        } else {
            marketOrder.setOrderSide(OrderSide.SELL);
        }
        orderDirectory.addOrder(marketOrder);
        // 
        BaseMessage bm = mf.orderMktOrder(orderId, instrument,
                Math.abs(quantity), quantity > 0 ? OrderSide.BUY : OrderSide.SELL, 0);
        send(bm);
        // 
        sendOrderSubmittedEvent(instrument, marketOrder);
        // 
        return orderId;
    }

    /**
     *
     * @param instrument
     * @param price
     * @param quantity signed quantity to be ordered
     * @return the internal order id.
     */
    public String sendLimitOrder(String instrument, Double price, Double quantity) {
        // 
        String orderId = "ID" + utsg.now().getNanoseconds();

        // we'll also construct a stop order. 
        LimitOrder limitOrder = new LimitOrder();
        limitOrder.setOrderId(orderId);
        limitOrder.setTradInstId(instrument);
        limitOrder.setLimitPrice(price);
        limitOrder.setQuantity(quantity);
        limitOrder.setOpenQuantity(quantity);
        if (Math.signum(quantity) == 1) {
            limitOrder.setOrderSide(OrderSide.BUY);
        } else {
            limitOrder.setOrderSide(OrderSide.SELL);
        }
        orderDirectory.addOrder(limitOrder);

        BaseMessage bm = mf.orderLimitOrder(orderId, instrument,
                Math.abs(quantity), price, quantity > 0 ? OrderSide.BUY : OrderSide.SELL, 0);
        send(bm);

        sendOrderSubmittedEvent(instrument, limitOrder);

        return orderId;
    }

    private void sendOrderSubmittedEvent(String instrument, Order order) {
        OrderSubmittedEvent ose = new OrderSubmittedEvent();
        ose.setRefOrderId(order.getOrderId());
        ose.setRefOrder(order);
        ose.setOptionalInstId(instrument);
        ose.setTimeStamp(new TimeStamp());
        this.getOrderEvent().fire(ose);
    }

    /**
     *
     * @param instrument
     * @param price
     * @param quantity signed quantity to be ordered
     * @return the internal order id.
     */
    public String sendStopOrder(String instrument, Double price, Double quantity) {
        String orderId = "ID" + utsg.now().getNanoseconds();

        // we'll also construct a stop order. 
        StopOrder stopOrder = new StopOrder();
        stopOrder.setOrderId(orderId);
        stopOrder.setTradInstId(instrument);
        stopOrder.setStopPrice(price);
        stopOrder.setQuantity(quantity);
        if (Math.signum(quantity) == 1) {
            stopOrder.setOrderSide(OrderSide.BUY);
        } else {
            stopOrder.setOrderSide(OrderSide.SELL);
        }
        stopOrder.setOpenQuantity(quantity);
        orderDirectory.addOrder(stopOrder);

        // 
        BaseMessage bm = mf.orderStopOrder(orderId, instrument,
                Math.abs(quantity), price, quantity > 0 ? OrderSide.BUY : OrderSide.SELL, 0);
        send(bm);
        sendOrderSubmittedEvent(instrument, stopOrder);
        return orderId;
    }

    public void updateLimitOrder(String orderId, double newPrice, double newQuantity) {
    }

    public void updateStopOrder(String orderId, double newPrice, double newQuantity) {
    }

    public void updateMarketOrder(String orderId, double newQuantity) {
    }

    /**
     * Use this to cancel an order.
     *
     * @param orderId
     */
    public void cancelOrder(String orderId) {
        String cancelOrderId = "ID" + utsg.now().getNanoseconds();
        SingleLegOrder slo = (SingleLegOrder) orderDirectory.getOrder(orderId);
        BaseMessage ocr = mf.OrderCancelRequest(cancelOrderId, orderId, slo.getTradInstId(), slo.getOrderSide(), Math.abs(slo.getQuantity()));
        send(ocr);
        // let's also send out the order cancellation submitted event. 
        OrderCancelSubmittedEvent ocse = new OrderCancelSubmittedEvent();
        ocse.setRefOrder(slo);
        ocse.setRefOrderId(orderId);
        ocse.setOptionalInstId(slo.getTradInstId());
        ocse.setTimeStamp(new TimeStamp());
        this.getOrderEvent().fire(ocse);
    }
}
