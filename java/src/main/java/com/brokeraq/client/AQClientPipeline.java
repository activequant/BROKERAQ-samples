package com.brokeraq.client;

import java.util.Deque;

import org.jboss.netty.channel.ChannelPipeline;
import org.jboss.netty.channel.ChannelPipelineFactory;
import org.jboss.netty.channel.Channels;
import org.jboss.netty.handler.codec.protobuf.ProtobufDecoder;
import org.jboss.netty.handler.codec.protobuf.ProtobufEncoder;
import org.jboss.netty.handler.codec.protobuf.ProtobufVarint32FrameDecoder;
import org.jboss.netty.handler.codec.protobuf.ProtobufVarint32LengthFieldPrepender;
import org.jboss.netty.handler.timeout.IdleStateHandler;
import org.jboss.netty.util.HashedWheelTimer;
import org.jboss.netty.util.Timer;

import com.activequant.messages.AQMessages;
import com.google.protobuf.ExtensionRegistry;

/**
 * The client pipeline defines the processing chain ("pipeline") for 
 * incoming and outgoing packets. Do not modify this unless you know what you
 * doing. 
 * 
 * @author GhostRider
 * 
 */
class AQClientPipeline implements ChannelPipelineFactory {
	/**
	 * Used for keeping track of time. 
	 */
	private final Timer timer = new HashedWheelTimer();
	
        @Override
	public ChannelPipeline getPipeline() throws Exception {

		ExtensionRegistry registry = ExtensionRegistry.newInstance();
		AQMessages.registerAllExtensions(registry);

		ChannelPipeline pipeline = Channels.pipeline();
		pipeline.addLast("idlestate", new IdleStateHandler(timer, 45, 45, 0));
		pipeline.addLast("idlestatehandler", new StaleConnectionSensor());
		pipeline.addLast("frameDecoder", new ProtobufVarint32FrameDecoder());
		pipeline.addLast("protobufDecoder", new ProtobufDecoder(
				AQMessages.BaseMessage.getDefaultInstance(), registry));
		pipeline.addLast("frameEncoder",
				new ProtobufVarint32LengthFieldPrepender());
		pipeline.addLast("protobufEncoder", new ProtobufEncoder());
		pipeline.addLast("handler", new AQClientHandler());
		return pipeline;
	}
}
