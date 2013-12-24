package com.brokeraq.client.model;

/**
 * The user session is a container to store username and password.
 *
 * @author ustaudinger
 */
public final class UserSession {

    /**
     * The username.
     */
    private String username;
    /**
     * The password in unencrypted form.
     */
    private String password;
    /**
     * the singleton pointer.
     */
    private static UserSession instance;

    /**
     * private constructor, please use the provided singleton method.
     */
    private UserSession() {
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public static UserSession instance() {
        if (instance == null) {
            instance = new UserSession();
        }
        return instance;
    }
}
