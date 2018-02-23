module QRGenerator 
open Suave.FunctionalViewEngine
open CommonHtml
open QRCoder
open Suave.Utils.Crypto
open System.Text
open FSharpx
open Types
open System

let encode size str = 
    use gen = new QRCodeGenerator()
    use dat = gen.CreateQrCode(str, QRCodeGenerator.ECCLevel.Q, forceUtf8=true)
    use code = new Base64QRCode(dat)
    code.GetGraphic(size)
        
let rand () = 
    let b = Array.zeroCreate<byte> 50
    cryptRandom.GetBytes b
    ASCIIEncoding.ASCII.GetString b

let base64Qr () = "data:image/gif;base64," + (rand () |> encode 3)

let page = {
    Title = "QR Code Generator" 
    Modified = DateTime(2018, 2, 22)
    Content = Nodes (fun () ->
        [
        div [class' "container mx-auto"] [
            div [class' "row"] [ 
                for _ in 0 .. 11 do yield div [class' "col-12 col-md-6 col-lg-4 col-xl-2"] [img [class' "align-middle mx-auto d-block"; src <| base64Qr ()]] 
            ]
        ]
    ] ) }