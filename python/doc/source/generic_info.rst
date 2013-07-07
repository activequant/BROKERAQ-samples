
Generic information
-------------------

In order to use our systems, you need to have a valid account, either a Demo or a Live account. Details on how to obtain a free Demo account are given in section “Getting an account” on page 4.

The API connects to an access gateway, which routes orders through to the market place.

The API uses two separate connections, one to receive price and another one for order related data. The price related connection is identified as “PRICE” and the order related connection is called “TRADE”. These identifiers are required while establishing connections. You can log in multiple times concurrently.

Your API program references our python API classes and uses these classes. You can obtain the latest copy of our API from our GitHub page.

Please consult the API accompanying readme file for latest information about prerequisites and how to install necessary dependencies. Note, if you are using Python a bit more often, chances are high you have all dependencies in place and can start developing your program right away.

