# Welcome to the FrankenSite!

This site is an unholy mix of technologies and languages. Muahahaha! Inspired by stories like TheDailyWTF (link to that competition to build a bad calc) and my own desire to learn many newer technologies (Docker, new Java, Swift, Postgres and NoSQL DB, Haskell, F#, Scala/Kotlin, Redis, yadayada), I present this dreeeary, horrid monster of a site! Some code may be copied. Directly from the Internet! 
Worse, all code will look kinda functional! And like I wrote it! AHHHHHHH!!!

## Let's peek inside the first Kotlin coffin...

## Hacking a Morgue Database with Haskell

Get started!

Impressions so far: Haskell has become easier to work with since last time I tried in early 2017. It looks like commercial interest has increased, with a few [powerful backers](https://www.fpcomplete.com/). Cabal has been overturned? by [stack](https://docs.haskellstack.org/en/stable/README/) and [stackage], including Long-Term Support (LTS) groups of packages

Let's see what's new for Haskell in VSCode. Looks like there is an extension that can enable a sort of Intellisense for Haskell code. We'll need to build [intero](), a metadata provider for Haskell source, ourselves first though
Aaand we run into our first issue: the default `stack build` command fails. After some poking around and looking at the stack trace, it seems like some files or folders are not being created in the right place. With even more poking, it looks like some of the folders are hitting the [260 character limit in Windows]. It's $CURRENT_YEAR$, why is this not fixed yet?? The simple solution seems to be to move the entire project to a folder with a shorter path.

use that futurama Tales of the Spooky Door or w/e

create a page that allows random combinations of different technologies

generate pokemon using Generative Adversial Neural Networks with Rrrrr - Pokemon as a Service (PaaS)

## Pythons on a Plane

## Go-ing for Help

## C-ing a Way out of this Go-ooo

## Let's give our Zombie Server Braaaiiins!!!
Using machine learning to pick on things in website database, like text/content generation

Use GraphQL and Apollo to tie together all the different web services

TODO: allow full-text search, maybe by generating all the pages and pushing them in a Lucene database or sqlite db

full-text should include only certain relevant portions of pages - <p> and <title> and whatnot
add clustering to allow for generation of tags

Articles should include timestamp, probably need an Article datatype, with a function to produce a page

add 'sample API' - for job search stuff

Hire Me! = Resume

Adventures in the Land of Polyglottony - a series of articles with implementations of web servers in different languages - the servers can also dish up something that is algorithmically interesting, like AI algorithms
a whole series, have testing and set-up scripts as well - include anthropomorphisms for each language as an introduction - Cobol, a dinosaur's dinosaur
curated links instead

an article about the seeming immune response developers seem to have to SQL within their codebases. How SQL, a declarative DSL, is replaced all too quickly with imperative bug-ridden solutions. The many instances where devs spent considerable time implementing different ways to not have to write small amounts of SQL. Entity framework, 

shameless plugs for different good NuGet packages