module Articles
open CommonHtml
open Suave.FunctionalViewEngine

let main () =
    template "All Articles" [
        h2 [class' "text-center"] [rawText "All Articles"]
        div [] [
            rawText "This will contain links to all articles"
        ]
    ]

let inaugaral () = 
    template "Article Introductory" [
        div [] [
            rawText "This is the first article"
        ]
    ]