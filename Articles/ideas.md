write a short article about dotnet Core and dotnet script - https://github.com/filipw/dotnet-script

Remember, anything that may be difficult in one language can always be turned into a webservice call into another one

Article server as well - we can build these using HTML instead - or React

Need some MSIL writing or on-the-fly compiling of some source code

We'll need some way to script/run all the different items, and unify the build/deploy process. This should include standing up the database

create a custom tool in `blah` to transform markdown files into HTML with our site's css tags - already exists https://github.com/showdownjs/showdown

need robots.txt, create from scanning site automatically

side articles about what I've been reading 
    The Shallows

links should be curated, with a bit of fluff describing why I have selected such a link

create a css to .net string generator/binder, for Bootstrap classes

article about why purity is such an important concept

compare programming languages and embracing language diversity, especially smaller "bets", to stocks and investing. how it's good to have diversity 

state and whitelisting and blacklisting - a comparison of how state is treated between functional and imperative/oop languages/paradigmes
in FL mutable state is effectively whitelisted - here is the enumerated set of values that we will changing at this particular scope/abstraction level. no more, possibly less
with IL mutable state must be blacklisted - practically everything is mutable, and within a particular scope, most data ABOVE that scope is also accessible and mutable - especially global variables. non-state data must be explicitly blacklisted by creating immutable objects instead - this is not the default