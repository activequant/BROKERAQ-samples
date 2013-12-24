/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.brokeraq.client.model;

import com.activequant.domainmodel.trade.order.Order;
import java.util.HashMap;
import java.util.Map;

/**
 * The order directory keeps track of all existing orders in the system and can
 * be used to share orders across components. This order directory is maintained
 * by the black box implementation.
 *
 * @author ustaudinger
 */
public class OrderDirectory {

    private Map<String, Order> orderMap = new HashMap<String, Order>();
    private static Object lock = new Object();
    private static OrderDirectory instance;

    private OrderDirectory() {
    }

    public static OrderDirectory instance() {
        synchronized (lock) {
            if (instance == null) {
                instance = new OrderDirectory();
            }
            return instance;
        }
    }

    public Order getOrder(String id) {
        return orderMap.get(id);
    }

    public void addOrder(Order order) {
        orderMap.put(order.getOrderId(), order);
    }

    public void deleteOrder(String orderId) {
        orderMap.remove(orderId);
    }
}
