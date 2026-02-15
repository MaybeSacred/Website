module PortfolioBalancer

open CommonHtml
open Suave.FunctionalViewEngine
open Types
open System

let ``portfolio balancer`` = {
    Title = "Portfolio Balancer"
    Created = DateTime.Now
    Modified = DateTime(2018, 5, 27)
    Content = textify
        [
            h2 [class' "text-center"] [rawText "Financial Portfolio Balancer"]
            div [id' "root"] []
            script [src "/dist/portfolio-balancer.bundle.js"] []
        ] }

let ``react playground`` = {
    Title = "React-Redux Playground"
    Created = DateTime.Now
    Modified = DateTime(2018, 6, 28)
    Content = textify
        [
            h2 [class' "text-center"] [rawText "All Articles"]
            div [id' "root"] []
            script [src "/dist/app.bundle.js"] []
        ] }

let ``pi website`` = {
    Title = "Pi Website"
    Created = DateTime.Now
    Modified = DateTime(2026, 2, 14)
    Content = textify
        [
            h2 [class' "text-center"] [rawText "Pi Config"]
            script [
                src "/dist/assets/index.js"
                attr "type" "module"
                flag "crossorigin"
                ] []
            // link [
            //     attr "rel" "stylesheet"
            //     attr "href" "/assets/index-DVB8kM4A.css"
            //     flag "crossorigin"
            //     ]
            div [id' "app"] []
        ] }