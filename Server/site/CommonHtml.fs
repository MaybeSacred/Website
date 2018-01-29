module CommonHtml
open Suave.FunctionalViewEngine
open MoreLinq

let id' = attr "id"
let class' = attr "class"
let href = attr "href"
let src = attr "src"
let cssLink s = link [attr "rel" "stylesheet"; attr "type" "text/css"; href s] 
let anchor' text title url = a [href url; attr "title" title] [RawText text]
let anchor text url = anchor' text text url
let programmingLinks = [
    """www.learnyouahaskell.com""", "Learn You a Haskell for Great Good!"
    """https://fsharpforfunandprofit.com""", "F# for Fun and Profit!"
    """http://sijinjoseph.com/programmer-competency-matrix/""", "Programmer Competency Matrix"
    """http://www.ycombinator.com/""", "Y Combinator"
    """https://gusty.github.io/FSharpPlus/abstractions.html""", "Common Functional Abstractions"
    """https://drboolean.gitbooks.io/mostly-adequate-guide/""", "A Mostly-Adequate Guide to Functional Programming"
    """https://www.random.org/""", "RANDOM.ORG"
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
    Paths.resume, "Resume"
    Paths.``qr-generator``, "QR Generator"
    Paths.``license-generator``, ".NET License Generator"
    Paths.about, "About"
]

let renderLinks links = [ for url,link in links do yield! [a [attr "href" url; attr "title" link] [RawText link]; br [] ]]

let linkBar () = 
    seq {
        yield h3 [] [RawText "Navigation"] 
        yield! renderLinks mainLinks 
        yield h3 [] [RawText "Programming Links"]
        yield! MoreEnumerable.RandomSubset(programmingLinks, 5) |>  renderLinks 
        yield h3 [] [RawText "Fun Links"]
        yield! MoreEnumerable.RandomSubset(funLinks, 5) |> renderLinks
    } |> List.ofSeq
    |> div [class' "linkSideBar"]
// TODO: allow full-text search, maybe by generating all the pages and pushing them in a Lucene database or sqlite db
// full-text should include only certain relevant portions of pages - <p> and <title> and whatnot
// add clustering to allow for generation of tags
// Articles should include timestamp, probably need an Article datatype, with a function to produce a page
// add 'crappy API'
// create navbar - this should include main links like About, Hire Me, etc, Search, Logo, and main blog title
let template title' content = 
    html [] [
        head [] [
            title [] [rawText title']
            meta [attr "charset" "utf-8"]
            meta [attr "name" "viewport"; attr "content" "width=device-width, initial-scale=1, shrink-to-fit=no"]
            cssLink """https://fonts.googleapis.com/css?family=Open+Sans"""
            cssLink "bootstrap.min.css"
        ]
        body [] [
            div [class' "container-fluid"] [
                div [class' "row justify-content-center"] [
                    div [class' "col align-self-center"; id' "corner"] [img [src "corner128.png"]]
                    div [class' "col-8 align-self-center"] [h1 [id' "title"] [rawText title']]
                    div [class' "col"] [h1 [id' "title"] [rawText title']]
                ]
                div [class' "row justify-content-center"] [
                    div [class' "col"] [linkBar ()]
                    div [class' "col-8"] content
                    div [class' "col"] [rawText "Quotes Quotes Quotes"]
                ]
            ]
            footer [class' "footer"] [
                    div [class' "links"] [
                        RawText "Built with "
                        anchor' "F#" "Main site for F#" "http://fsharp.org"  
                        RawText ", "
                        anchor' "Suave.IO" "A simple self-hosting webserver for F#" "http://suave.io"  
                        RawText ", and a little love"
                    ]
                    div [class' "themes"] [
                        button [] [RawText "Change theme"]
                    ]
                
            ]
            script [src """https://code.jquery.com/jquery-3.2.1.slim.min.js"""; attr "crossorigin" "anonymous"] []
            script [src """https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"""; attr "crossorigin" "anonymous"] []
            script [src """https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.3/js/bootstrap.min.js"""; attr "crossorigin" "anonymous"] []
        ]
    ]