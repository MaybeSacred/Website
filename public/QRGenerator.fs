module QRGenerator 
open Suave.FunctionalViewEngine
open CommonHtml
open QRCoder
open Suave.Utils.Crypto
open System.Text
open FSharpx

let encode size str = 
    use gen = new QRCodeGenerator()
    let dat = gen.CreateQrCode(str, QRCodeGenerator.ECCLevel.Q)
    use code = new Base64QRCode(dat)
    code.GetGraphic(size)
        
let rand () = 
    let b = Array.zeroCreate<byte> 50
    cryptRandom.GetBytes b
    UTF8Encoding.UTF8.GetString b 
    |> String.substring' 0 40

let base64Qr () = "data:image/gif;base64," + (rand () |> encode 3)

let page () = 
    template "QR Code Generator" [
        table [] [
            tr [] [ for _ in 0 .. 4 do yield td [class' "qr"] [img [class' "qr"; attr "src" <| base64Qr ()]] ]
            tr [] [ for _ in 0 .. 4 do yield td [class' "qr"] [img [class' "qr"; attr "src" <| base64Qr ()]] ]
        ]
    ]
