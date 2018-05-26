module FableApp

open Fable.Core
open Fable.Core.JsInterop
open Fable.Import
open Common.Say

let init() =
    let canvas = Browser.document.getElementsByTagName_canvas().[0]
    canvas.width <- 1000.
    canvas.height <- 800.
    let ctx = canvas.getContext_2d()
    // The (!^) operator checks and casts a value to an Erased Union type
    // See http://fable.io/docs/interacting.html#Erase-attribute
    ctx.fillStyle <- !^ "rgb(200,0,0)"
    ctx.fillRect (10., 10., 70., 500.)
    ctx.fillStyle <- !^ "rgba(0, 0, 200, 0.5)"
    ctx.fillRect (40., 60., 70., 150.)
    let h3 = Browser.document.createElement_h3() 
    h3.textContent <- "My own freaking header"
    h3 |> Browser.document.body.appendChild |> ignore

init()