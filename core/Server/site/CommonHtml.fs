module CommonHtml
open Suave.FunctionalViewEngine
open MoreLinq
open Types

let id' = attr "id"
let class' = attr "class"
let href = attr "href"
let src = attr "src"
let title' = attr "title"
let style' = attr "style"
let br' = br []
let cssLink s = link [attr "rel" "stylesheet"; attr "type" "text/css"; href s] 
let anchor' text title url = a [href url; title' title] [RawText text]
let anchor text url = anchor' text text url
let paragraph = rawText >> List.singleton >> p []

let domainName = "tysonontech.sytes.net"

let pictureLinks = [
    """https://i.redd.it/vn4lx6ymivi11.jpg""","""https://www.reddit.com/r/EarthPorn/comments/9b16vn/the_zion_narrows_ut_oc_3024_x_4032_one_of_many/"""
    """https://i.redd.it/9e735ke272j11.jpg""","""https://www.reddit.com/r/EarthPorn/comments/9bat8f/holyhead_wales_oc_the_three_and_half_hour_boat/"""
    """https://i.redd.it/9ipxsp81lwi11.jpg""","""https://www.reddit.com/r/EarthPorn/comments/9b32c2/berg_lake_mount_robson_provincial_park_british/"""
    """https://i.redd.it/12iybvp1oxi11.jpg""","""https://www.reddit.com/r/EarthPorn/comments/9b4ryw/a_magical_sunset_over_monument_valley_utah/"""
    """https://i.redd.it/vr4g5yblpwi11.jpg""","""https://www.reddit.com/r/EarthPorn/comments/9b3af5/morning_burn_yosemite_np_3654x5473_oc/"""
    """https://i.redd.it/jcxje1cvh0j11.jpg""","""https://www.reddit.com/r/EarthPorn/comments/9b85vl/evening_light_over_the_ehrwalder_alm_austria_oc/"""
]
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
    """http://reactivex.io""", "Reactive Extensions"
]
let funLinks = [
    """http://www.juliawertz.com/""", "Julia Wertz"
    """https://xkcd.com/""", "XKCD"
    """https://smbc-comics.com/""", "Saturday Morning Breakfast Cereal"
    """http://www.last-halloween.com/""", "The Last Halloween"
    """http://www.dumbingofage.com/""", "Dumbing of Age"
    """https://engaging-data.com/""","Engaging Data"
]
let mainLinks = [
    Paths.home, "Home"
    Paths.``qr-generator``, "QR Generator"
    Paths.resume, "Resume"
    //Paths.articles, "Articles"
    Paths.about, "About"
]

let quotes = [
    [rawText "So you run and you run to catch up with the sun but it's sinking"
     br []
     rawText "Racing around to come up behind you again."
     br []
     rawText "The sun is the same in a relative way but you're older,"
     br []
     rawText "Shorter of breath and one day closer to death"], "Pink Floyd - Time"
    [rawText "Jon feed Bronx and walk Bronx every day and love Bronx. Bronx best boy, but Jon good boy too"], "Bronx, my Dog"
    [rawText "Give me a lever long enough, and a place to stand, and I will move the earth"], "Archimedes"
    [rawText "I started out with nothing and I still got most of it left"], "Tom Waits"
    [rawText "Life - and I don't suppose I'm the first to make this comparison - is a disease: sexually transmitted, and invariably fatal"],"Neil Gaiman - Death"
    [rawText "The price of anything is the amount of life you exchange for it"], "Henry David Thoreau"
    [rawText """"Don’t gamble"; take all your savings and buy some good stock, and hold it till it goes up, then sell it. If it don’t go up, don’t buy it"""],"Will Rogers"
    [rawText "You been tellin' me you're a genius"
     br []
     rawText "Since you were seventeen"
     br []
     rawText "In all the time I've known you"
     br []
     rawText "I still don't know what you mean"], "Steely Dan"
]

let quoteBar () =
    // get Bronk pic, make that quote go together
    // fire emblem and pokemon
    let quote, author = quotes.RandomSubset 1 |> Seq.head
    let pic = pictureLinks.RandomSubset 1 |> Seq.head |> fst
    [
        img [src pic; class' "img-fluid p-2 d-block"]
        blockquote [ class' "blockquote text-center small"; ] [
            p [attr "style" "font-size: .7em"] quote
            footer [ class' "blockquote-footer"; ] [rawText author]
        ]
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
            link [ attr "rel" "shortcut icon"; attr "type" "image/x-icon"; href "favicon.ico"; ]
        ]
        body [] [
            header [class' "navbar navbar-expand-md navbar-dark bg-primary justify-content-between py-1"; ] [
                div [class' "navbar-brand"; ] [
                    div [class' "row align-items-center p-0"] [
                        div [class' "col px-1 py-0"] [a [href domainName; title' "Home"] [img [src "logo.png"; class' "img-fluid"; attr "width" "48"; title' "Logo"]]]
                        div [class' "col px-1 py-0"] [rawText "Tyson on Tech"]
                    ]
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
                    div [ class' "col-12 col-sm-3 col-xl-2 my-2 px-1"; ] [
                        ul [ class' "list-group list-group-flush"; ] [linkBar ()]
                    ]
                    div [ class' "col-12 col-sm-6 col-xl-8 my-3"; ] (
                        match content with
                        | Text s -> [rawText s]
                        | Nodes s -> s ()
                    )
                    div [ class' "col-12 col-sm-3 col-xl-2 my-2 px-1"; ] <| quoteBar ()
                ]
            ]
            footer [ class' "footer"; ] [
                div [ class' "container-fluid"; ] [
                    div [ class' "row justify-content-center bg-dark"; ] [
                        div [ class' "col text-center"; ] [
                            p [class' "text-light"] [
                                rawText "Built with "
                                a [ href "http://fsharp.org"; class' "text-info"; title' "Main site for F#"; ] [rawText "F#"]
                                rawText ", "
                                a [ href "http://suave.io"; class' "text-info"; title' "A simple self-hosting webserver for F#"; ] [rawText "Suave.IO"]
                                rawText ", and a little love. "
                                a [ href "https://github.com/MaybeSacred/Website"; class' "text-info"; title' "Source code for this site"; ] [rawText "Source code available on GitHub"]
                                rawText ". "
                                a [ href "https://aws.amazon.com/ec2/"; class' "text-info"; title' "Amazon EC2"; ] [rawText "Hosted on AWS"]
                            ]
                        ]
                    ]
                ]
            ]
            script [ src "https://code.jquery.com/jquery-3.3.1.slim.min.js"; attr "integrity" "sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo"; attr "crossorigin" "anonymous"; ] []
            script [ src "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js"; attr "integrity" "sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49"; attr "crossorigin" "anonymous"; ] []
            script [ src "https://stackpath.bootstrapcdn.com/bootstrap/4.1.2/js/bootstrap.min.js"; attr "integrity" "sha384-o+RDsa0aLu++PJvFqy8fFScvbHFLtbvScb8AjopnFD+iEQ7wo/CG0xlczd+2O/em"; attr "crossorigin" "anonymous"; ] []
        ]
    ]
