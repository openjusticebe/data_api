CHANGELOG
=========

This changelog references the relevant changes done in this project.

This project adheres to [Semantic Versioning](http://semver.org/) 
and to the [CHANGELOG recommendations](http://keepachangelog.com/).
## Alpha Development
### [10] - (XXX)
[todo]
- attribute ark to new documents
- store arks in database
- link documents to terms through voc\_api support
- expose ark ID's through API

### [9] - (2021-12-07)
- fixing user upload bug when using account instead of key
- adding query user by email method

### [8] - (2021-03-31)
- mail server timeout hotfix

### [7] - (2021-03-09)
- refactored auth part
- removed unneeded dependencies
- adding ECLI access to multiple formats (txt, pdf, latex)

### [6] - (2021-03-02)
- added latex and pdf conversion
- added links to pdf and text versions
- added basic latex document template
- added pdf link to notification email
- added pdf as attachment to notification mail

### [5] - (2021-02-27)
- added author information in edit screen
- added send mail capability
- added mail notifications and first templates
- added view counters in record, and functionality
- added limited viewability for hash (personnal) links
- refactored auth code
- added warning if no information about appeal

### [4] - (2021-02-15)
- refactoring code, using routes to separate functionnality
- adding OAuth support for authenticating users
- added interfaces for reviewing and updating content

### [3] - (2021-01-21)
- support for appeal indicator
- support for upload of document links (doclink)
- switch to single version indicator

### [0.2.1] - (2020-12-01)
- added labels endpoint
- added labels database schema
- storing user-defined labels in database


### [0.2.0] - (2020-11-21)
- updated hashing algorithm
- fixed airtable key verification
- improved HTML rendering (hash and ecli endpoints)
- added list endpoint for ecli navigation
- added document language attribute
- DB Schema Update `add_lang.sql`


### [0.1.0] - (2020-11-13)
- Added changelog
- First Commit !
