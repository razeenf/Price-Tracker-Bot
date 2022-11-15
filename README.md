# Amazon Price Tracker Discord Bot 

A simple to use Discord bot that helps you track Amazon.ca products for price drops. Simply give the bot a link of the product you wish to track along with your email and It'll notify you through email when the product goes on sale. 

### List of Commands:
* !help
* !track <<e>email address> <<e>amazon link>
* !stop <<e>amazon link>

## How it Works

When the **!track** command is used the bot obtains the users email address, ASIN userID and channelID. It then stores these values and the current product price into a document on MonogDB, if the ASIN already exists in the database the users details will be appended to the coressponding documents user-info array so multiple users can be tracking the same product. 

The **!stop** command allows users to stop tracking a product, it requires the amazon link as input so that the bot can query the database and find the product ASIN if it exists and remove the users details from the list if they were tracking it, now that user won't be notified for if that product goes on sale. If the user-info list is emtpy the document is deleted so that the product isn't being tracked for nobody. 

Every few minutes the program loops through the documents, obtains the ASIN values, scrapes the current prices on the Amazon site and compares it to the price written on file. If there is price drop all users tracking the product will be notified through a ping on discord and an email is created using an HTML template and is then sent out using the Gmail API to all users. The associated document is then deleted from the database.

This project utilizes Asynchronous Web Scraping, MonogDB, Gmail API and Discord API. It's containerized with Docker and hosted on AWS EC2.

## Preview
<p align="center">
  <img src="demo/discord.png"><br>
  <img src="demo/email.png">
</p>
