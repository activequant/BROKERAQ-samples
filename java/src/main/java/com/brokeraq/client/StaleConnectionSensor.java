package com.brokeraq.client;

import java.util.logging.Logger;

import org.jboss.netty.channel.ChannelHandlerContext;
import org.jboss.netty.handler.timeout.IdleState;
import org.jboss.netty.handler.timeout.IdleStateAwareChannelHandler;
import org.jboss.netty.handler.timeout.IdleStateEvent;

/**
 * This sensor checks whether a netty connection is stale or not.
 *
 * @author ustaudinger
 */
class StaleConnectionSensor extends IdleStateAwareChannelHandler {

    private static final Logger log = Logger.getLogger(StaleConnectionSensor.class.getName());

    @Override
    public void channelIdle(ChannelHandlerContext ctx, IdleStateEvent e) {
        if (e.getState() == IdleState.READER_IDLE) {
            log.info("Incoming stream is idle.");
            e.getChannel().close();
        }
    }
}
