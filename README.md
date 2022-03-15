# Website Analutics for Klimatriksdagen.se

## Todo: 

- [x] Create prototype JS code to post events 
- [ ] Define what events needs to be sent 
- [ ] Define schema for analytics events  
- [ ] Set up Sink CDK project, stack and deployment strategy
- [ ] Build and test data sink for collecting events
- [ ] Finalize JS events and deploy data sink

## Web analytics 

Interesting questions to answer are:


### Website traffic
- How is total website traffic fluctuating by day and by week? 
- How is website sessions fluctuating by day and by week?
- How many unique users visit the site by day and by week?
- What is the ratio of one-event-sessions vs multiple-event-sessions?
- What is the average number of page loads per session?
- How long is average time on page?
- How long is an average session (for sessions with more than one page load)?
- How does website traffic fluctuate during the day on average?
- How does website traffic fluctuate during the week on average?

### Page statistics 
- What pages are the most common start of each session?
- What pages are the most common end of each session?
- What pages has the longest read time?
- What pages are most common visisted pages overall?
- What pages are the most common visisted pages over sessions? 
- What pages are the most common visisted pages over unique users? 

### Motion statistics 
- What motions are most common visisted motions overall?
- What motions are the most common visisted motions over sessions? 
- What motions are the most common visisted motions over unique users? 

### Geolocation
- How does the distribution of countries look like for unique users?
- How does the distribution of cities look like for unique users?
- When splitting distributions of cities in 6 top cities + others, how is this developing over time?
- When splitting distributions of countries in 6 top countries + others, how is this developing over time?

### Devie type
- What is the distribution between desktop and mobile for overall events?
- What is the distribution between desktop and mobile for sessions?
- What is the distribution between desktop and mobile for unique users?
- What is the ratio of one-event-sessions to multiple-event-sessions on desktop versus mobile?
- What is the average number of events per session on desktop versus mobile?
- How long is an average session (for sessions with more than one page load) on desktop versus mobile?
**Consider doing page statistics split between desktop and mobile**

