module Articles
open CommonHtml
open Suave.FunctionalViewEngine

let main () =
    template "Articles" [
        div [] [
            rawText "This will contain links to all articles"
        ]
    ]

let inaugaral () = 
    template "Article introductory" [
        div [] [
            rawText "This is the first article"
        ]
    ]