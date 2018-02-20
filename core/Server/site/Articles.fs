﻿module Articles
open CommonHtml
open Suave.FunctionalViewEngine

let ``qr-codes`` () = 
    template "QR Codes for Pokemon" [
        div [] [
            rawText "This is the first article"
            a [title' "By en:Game Freak, en:Nintendo, en:The Pokémon Company (Transferred from en.wikipedia to Commons.) [Public domain], via Wikimedia Commons"; href "https://commons.wikimedia.org/wiki/File%3AInternational_Pok%C3%A9mon_logo.svg"] [
                img [attr "width" "256"; attr "alt" "International Pokémon logo"; src "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Pok%C3%A9mon_logo.svg/256px-International_Pok%C3%A9mon_logo.svg.png"]
            ]
        ]
    ]

let articles = 
    dict [
        "inaugaral", ``qr-codes``
    ]

let main () =
    template "All Articles" [
        h2 [class' "text-center"] [rawText "All Articles"]
        div [] [ for i in articles do yield anchor i.Key "This will contain links to all articles" ]
    ]