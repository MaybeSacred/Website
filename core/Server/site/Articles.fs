module Articles
open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System
open QRGenerator

let articles = 
    dict [
        "inaugaral", QRGenerator.``making-a-qr-code-generator``
    ]

let main = {
    Title = "All Articles" 
    Created = DateTime.Now
    Modified = DateTime(2018, 2, 22)
    Content = textify
        [
            h2 [class' "text-center"] [rawText "All Articles"]
            div [] [ for i in articles do yield anchor i.Value.Title (Paths.articles + "/" + i.Key) ]
        ] }