# BankChurn
Project to grab Trustpilot reviews (using scrapy), add Vader sentiment scores (TP stars to validate), and visualise in a plotly Dash

0: Required packages in requirements.txt

1: Pull Reviews from Trustpilot:

The spider to pull the info from Trustpilot is in the tp_scrapy folder. Info on settings etc, where the data is being written to etc are in this folder.

The spider itself is in: tp_scrapy/spiders/TPspider.py

In the root directory, open terminal: scrapy crawl TPGrabReviews

Generates TrustPilot.jl and TrustPilot.json with the reviews.

2: Add Vader sentiment scores:
See AddSentimentToReviews.py in the root directory
Run .py file to add sentiments to reviews and output sentimentdata.csv

3: Visualise in plotly Dash:
See app.py

In root directory, open terminal: python app.py

Will run and produce a link. Open and see the (WIP) interacive plotly dash

