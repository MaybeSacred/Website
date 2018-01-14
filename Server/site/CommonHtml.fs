module CommonHtml
open Suave.FunctionalViewEngine

let cssLink s = link [attr "rel" "stylesheet"; attr "type" "text/css"; attr "href" s] 
let id' = attr "id"
let class' = attr "class"
let programmingLinks = [
    """learnyouahaskell.com""", "Learn You a Haskell for Great Good!"
    """fsharpforfunandprofit.com""", "F# for Fun and Profit!"
    """http://sijinjoseph.com/programmer-competency-matrix/""", "Programmer Competency Matrix"
    """http://www.ycombinator.com/""", "Y Combinator"
]
let funLinks = [
    """http://www.juliawertz.com/""", "Julia Wertz"
    """""", "XKCD"
    """""", "Saturday Morning Breakfast Cereal"
]
let mainLinks = [
    Paths.home, "Home"
    Paths.resume, "Resume"
    Paths.``qr-generator``, "QR Generator"
    Paths.``license-generator``, ".NET License Generator"
    Paths.about, "About"
]

let renderLinks links = [ for url,link in links do yield a [attr "href" url; attr "title" link] [RawText link; br []] ]

let linkBar = 
    seq {
        yield h3 [] [RawText "Navigation"] 
        yield! renderLinks mainLinks 
        yield h3 [] [RawText "Programming Links"]
        yield! renderLinks programmingLinks 
        yield h3 [] [RawText "Fun Links"]
        yield! renderLinks funLinks
    } |> List.ofSeq
    |> div [class' "linkSideBar"]

let template title' content =
    html [] [
        head [] [
            title [] [rawText title']
            cssLink """https://fonts.googleapis.com/css?family=Open+Sans"""
            cssLink "output.css"
        ]
        body [] [
            div [class' "divTable purpleHorizon"] [
                div [class' "divTableHeading"] [
                    div [class' "divTableRow"] [
                        div [class' "divTableHead"; id' "corner"] [img [attr "src" "corner256.png"]]
                        div [class' "divTableHead"] [h1 [id' "title"] [rawText title']]
                    ]
                ]
                div [class' "divTableBody"] [
                    div [class' "divTableRow"] [
                        div [class' "divTableCell"] [linkBar]
                        div [class' "divTableCell"] content
                    ]
                ]
            ]
            div [id' "footer"] [
                div [class' "links"] [
                    RawText "Built with "
                    a [attr "href" "http://fsharp.org"; attr "title" "Main site for F#"] [RawText "F#"]
                    RawText " and "
                    a [attr "href" "http://suave.io"; attr "title" "A simple self-hosting webserver for F#"] [RawText "Suave.IO"]
                ]
            ]
        ]
    ]