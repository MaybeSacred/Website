module AccidentalDeveloper
open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System

let ``so you've gotten a job as a developer`` = { 
    Title = "Accidental Developer" 
    Created = DateTime.Now
    Modified = DateTime.Now
    Content = textify 
        [
            // security OWASP
            div [] [
                h2 [class' "text-center"] [rawText "Building a QR Generator for Pokémon"]
                br'
                a [title' "By en:Game Freak, en:Nintendo, en:The Pokémon Company (Transferred from en.wikipedia to Commons.) [Public domain], via Wikimedia Commons"; href "https://commons.wikimedia.org/wiki/File%3AInternational_Pok%C3%A9mon_logo.svg"; class' "img-responsive center-block"] [
                    img [attr "width" "256"; attr "alt" "International Pokémon logo"; src "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Pok%C3%A9mon_logo.svg/256px-International_Pok%C3%A9mon_logo.svg.png"]
                ]
                br'
                br'
                p [] [
                    rawText "   The newest generation of Pokémon games, "
                    a [href "https://www.serebii.net/ultrasunultramoon/"] [rawText "Sun and Moon and their Ultra counterparts"]
                    rawText """, have a 
                    feature where Pokémon not normally found within the game can be caught. This is called Island Scan. 
                    Interestingly, the game designers decided to add a twist: each activation of Island Scan requires 
                    scanning QR codes using the Nintendo DS camera. Ugh! The game designers were clever though, the 
                    games don't count scanning the same QR code multiple times, so you'll need many distinct codes if 
                    you intend to catch all x something Pokémon available through the Island Scan feature."""
                ]
                h4 [] [rawText "What's a poor programmer to do?"]
                paragraph """Make a randomized QR code generator, of course! TL;DR, That's exactly what I did. """
            ]
        ] }