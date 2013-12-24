package com.brokeraq.client;

import java.net.InetSocketAddress;
import java.util.concurrent.Executors;
import java.util.logging.Logger;

import org.jboss.netty.bootstrap.ClientBootstrap;
import org.jboss.netty.channel.Channel;
import org.jboss.netty.channel.ChannelFuture;
import org.jboss.netty.channel.socket.nio.NioClientSocketChannelFactory;

import com.activequant.interfaces.utils.IEventListener;
import com.activequant.messages.AQMessages;
import com.activequant.messages.AQMessages.BaseMessage;
import com.brokeraq.client.exceptions.ConnectionAttemptInProgress;
import java.util.logging.Level;

/**
 * Package visibility intended, do not use directly.
 *
 * @author ustaudinger
 */
class AQSocket {

    private static final Logger log = Logger.getLogger(AQSocket.class.getName());
    private String host = "78.47.96.150";
    private int port = 59999;
    private Channel channel;
    private ClientBootstrap bootstrap;
    private static AQSocket instance = null;
    private Thread t;
    private boolean connected = false;
    private BlackBoxImpl b = (BlackBoxImpl) BlackBoxImpl.instance();

    public void setConnected(boolean b) {
        connected = b;
    }

    /**
     * Returns whether the socket is connected or not.
     *
     * @return
     */
    public boolean isConnected() {
        return connected;
    }

    /**
     * Private constructor, plese use the instance.
     */
    private AQSocket() {
        //
        bootstrap = new ClientBootstrap(
                new NioClientSocketChannelFactory(Executors
                .newCachedThreadPool(), Executors
                .newCachedThreadPool()));
        bootstrap.setPipelineFactory(new AQClientPipeline());
        // 
        b.getOutgoingMessageEvent().addEventListener(internalListener);
    }

    static AQSocket instance() {
        if (instance == null) {
            instance = new AQSocket();
        }
        return instance;
    }

    void start() throws ConnectionAttemptInProgress {
        if (t == null || (!t.isAlive() && !isConnected())) {
            t = new Thread(new Runnable() {
                @Override
                public void run() {
                    //
                    ChannelFuture connectFuture = bootstrap
                            .connect(new InetSocketAddress(host, port));

                    // waiting in a blocking mode until we are connected.
                    channel = connectFuture.awaitUninterruptibly().getChannel();

                }
            });
            t.start();
        } else {
            throw new ConnectionAttemptInProgress();
        }
    }

    void stop() {
        channel.close();
    }

    private void send(BaseMessage bm) {
        log.log(Level.INFO, "Sending: {0}", bm);
        channel.write(bm);
    }
    private IEventListener<AQMessages.BaseMessage> internalListener = new IEventListener<AQMessages.BaseMessage>() {
        @Override
        public void eventFired(BaseMessage bm) {
            send(bm);
        }
    };
}
