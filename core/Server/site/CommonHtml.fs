module CommonHtml
open Suave.FunctionalViewEngine
open MoreLinq
open Types
open System.Collections.Generic

let id' = attr "id"
let class' = attr "class"
let href = attr "href"
let src = attr "src"
let title' = attr "title"
let br' = br []
let cssLink s = link [attr "rel" "stylesheet"; attr "type" "text/css"; href s] 
let anchor' text title url = a [href url; title' title] [RawText text]
let anchor text url = anchor' text text url
let paragraph = rawText >> List.singleton >> p []

let domainName = "tysonontech.sytes.net"

let programmingLinks = [
    """www.learnyouahaskell.com""", "Learn You a Haskell for Great Good!"
    """https://fsharpforfunandprofit.com""", "F# for Fun and Profit"
    """http://sijinjoseph.com/programmer-competency-matrix/""", "Programmer Competency Matrix"
    """http://www.ycombinator.com/""", "Y Combinator"
    """https://gusty.github.io/FSharpPlus/abstractions.html""", "Common Functional Abstractions"
    """https://drboolean.gitbooks.io/mostly-adequate-guide/""", "A Mostly-Adequate Guide to Functional Programming"
    """https://www.random.org/""", "RANDOM.ORG"
    """https://github.com/papers-we-love/papers-we-love""", "Papers We Love"
    """https://blog.acolyer.org/""", "the morning paper"
    """http://paulgraham.com/pypar.html""", "The Python Paradox"
    """http://blog.ploeh.dk/""", "ploeh blog"
    """http://quotes.cat-v.org/programming/""", "A Selection of Great Programming Quotes"
    """https://github.com/dhilipsiva/webapp-checklist""","Web Developer Checklist"
    """https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/""", "Things You Should Never Do"
]
let funLinks = [
    """http://www.juliawertz.com/""", "Julia Wertz"
    """https://xkcd.com/""", "XKCD"
    """https://smbc-comics.com/""", "Saturday Morning Breakfast Cereal"
    """http://www.last-halloween.com/""", "The Last Halloween"
    """http://www.dumbingofage.com/""", "Dumbing of Age"
]
let mainLinks = [
    Paths.home, "Home"
    Paths.``qr-generator``, "QR Generator"
    //Paths.``license-generator``, ".NET License Generator"
    //Paths.articles, "Articles"
    Paths.about, "About"
    //Paths.``portfolio-balancer``, "Portfolio Balancer"
    //Paths.``react-playground``, "React Playground"
]
let quotes = [
    "Jon feed Bronx and walk Bronx every day and love Bronx. Bronx best boy, but Jon good boy too", "Bronx, my Dog"
    """So you run and you run to catch up with the sun but it's sinking
Racing around to come up behind you again.
The sun is the same in a relative way but you're older,
Shorter of breath and one day closer to death""", "Pink Floyd - Time"
    "Give me a lever long enough, and a place to stand, and I will move the earth", "Archimedes"
    "I started out with nothing and I still got most of it left", "Tom Waits"
    "Life - and I don't suppose I'm the first to make this comparison - is a disease: sexually transmitted, and invariably fatal","Neil Gaiman - Death"
    "The price of anything is the amount of life you exchange for it", "Henry David Thoreau"
]
let quoteBar () =
    let quote, author = quotes.RandomSubset 1 |> Seq.head
    blockquote [ class' "blockquote text-center small"; ] [
        p [attr "style" "font-size: .9em"] [rawText quote]
        footer [ class' "blockquote-footer"; ] [rawText author]
    ]

let renderLinks links = [for url,link in links do yield! [div [class' "ml-2"] [a [href url; title' link; ] [RawText link]; br' ]]]

let linkBar () = 
    let li header fullLink links =
        seq {
            yield h5 [ class' "text-dark" ] [rawText header]
            yield! renderLinks links 
            yield! renderLinks [fullLink, "More..."] 
        } |> List.ofSeq
        |> li [ class' "list-group-item px-1"; ] 
    div [class' "linkSideBar"] [
        li "Site" Paths.sitemap mainLinks
        programmingLinks.RandomSubset 5 |> li "Programming Links" Paths.``all-programming-links``
        funLinks.RandomSubset 5 |> li "Fun Links" Paths.``all-fun-links`` 
    ]

let template { Title = title''; Content = content } =
    html [] [
        head [] [
            title [] [rawText title'']
            meta [ attr "http-equiv" "Content-Type";  attr "content" "text/html; charset=utf-8"; ]
            meta [ attr "name" "viewport";  attr "content" "width=device-width, initial-scale=1, shrink-to-fit=no"; ]
            ``base`` [href Paths.``base``] []
            cssLink "bootstrap.min.css"
            cssLink "site.css"
            link [ attr "rel" "shortcut icon";  href "fable.ico"; ]
        ]
        body [] [
            header [ class' "navbar navbar-expand-md navbar-dark bg-primary justify-content-between py-2"; ] [
                span [ class' "pb-0"; ] [
                    span [ class' "navbar-brand"; ] [rawText "Tyson on Tech"]
                ]
                div [ class' "collapse navbar-collapse";  id' "navbarNavAltMarkup"; ] [
                    div [ class' "navbar-nav"; ] [
                        a [ class' "nav-item nav-link";  href Paths.home; ] [
                            rawText "Home"                            
                            span [ class' "sr-only"; ] [rawText "(current)"]
                        ]
                        a [ class' "nav-item nav-link";  href Paths.about; ] [rawText "About"]
                        a [ class' "nav-item nav-link";  href Paths.sitemap; ] [rawText "Site Map"]
                    ]
                ]
                form [ class' "form-inline"; ] [
                    input [ class' "form-control mr-sm-2";  attr "type" "search";  attr "placeholder" "Search";  attr "aria-label" "Search"; ]
                    button [ class' "btn btn-outline-info my-2 my-sm-0";  attr "type" "submit"; ] [rawText "Search"]
                ]
                button [ class' "navbar-toggler";  attr "type" "button";  attr "data-toggle" "collapse";  attr "data-target" "#navbarNavAltMarkup";  attr "aria-controls" "navbarNavAltMarkup";  attr "aria-expanded" "false";  attr "aria-label" "Toggle navigation"; ] [
                    span [ class' "navbar-toggler-icon"; ] []
                ]
            ]
            div [ class' "container-fluid"; ] [
                div [ class' "row"; ] [
                    div [ class' "col-12 col-sm-3 col-xl-2 py-1 bg-light"; ] [
                        ul [ class' "list-group list-group-flush"; ] [linkBar ()]
                    ]
                    div [ class' "col-12 col-sm-6 col-xl-8 py-3"; ] (
                        match content with
                        | Text s -> [rawText s]
                        | Nodes s -> s ()
                    )
                    div [ class' "col-12 col-sm-3 col-xl-2 py-3 bg-light"; ] [quoteBar ()]
                ]
            ]
            footer [ class' "footer"; ] [
                div [ class' "container-fluid"; ] [
                    div [ class' "row justify-content-center bg-secondary"; ] [
                        div [ class' "col"; ] []
                        div [ class' "col-8 text-center"; ] [
                            p [] [
                                a [ href "https://github.com/MaybeSacred/Website";  title' "Source code for this site"; ] [rawText "Source code available on GitHub"]
                                rawText ". Built with "
                                a [ href "http://fsharp.org";  title' "Main site for F#"; ] [rawText "F#"]
                                rawText ", "
                                a [ href "http://suave.io";  title' "A simple self-hosting webserver for F#"; ] [rawText "Suave.IO"]
                                rawText ", and a little love"
                            ]
                        ]
                        div [ class' "col"; ] []
                    ]
                ]
            ]
            script [ src "https://code.jquery.com/jquery-3.3.1.slim.min.js"; attr "integrity" "sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"; attr "crossorigin" "anonymous"; ] []
            script [ src "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js"; attr "integrity" "sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49"; attr "crossorigin" "anonymous"; ] []
            script [ src "https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/js/bootstrap.min.js"; attr "integrity" "sha384-o+RDsa0aLu++PJvFqy8fFScvbHFLtbvScb8AjopnFD+iEQ7wo/CG0xlczd+2O/em"; attr "crossorigin" "anonymous"; ] []
        ]
    ]
