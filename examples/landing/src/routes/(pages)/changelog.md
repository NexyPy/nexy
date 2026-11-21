# Changelog

What changed in Beacon, newest first. Beacon is in private beta: these are the changes the people on
the waitlist will find when it opens.

## November 2026

### Status pages on your own domain

A status page can now answer on `status.yourdomain.com`. Add a CNAME record, and Beacon issues the
certificate.

- Pick which monitors a page shows, and in what order.
- Write an incident note once: it appears on the page and in the alert.

## October 2026

### Checks from six regions

Every check now runs from six regions. A monitor is only marked down when two of them agree, so a
bad route between one region and your server no longer wakes anyone up.

### Quieter alerts

- One alert per incident, then one when it is over, instead of one per failed check.
- Alerts that nobody acknowledges in 10 minutes go to the next person on call.

## September 2026

### First private beta

The first teams on the waitlist started watching their sites: HTTP and keyword checks every 30
seconds, alerts by email and chat, and 45 days of history.
