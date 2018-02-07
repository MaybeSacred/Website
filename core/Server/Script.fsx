#r @"C:\Users\jtyso\.nuget\packages\htmlagilitypack\1.6.15\lib\netstandard2.0\HtmlAgilityPack.dll"
#r """C:\Users\jtyso\.nuget\packages\netstandard.library\2.0.0\build\netstandard2.0\ref\netstandard.dll"""
open HtmlAgilityPack
open System.Text
open FSharp.Core
open System

let buildList (head:HtmlNode) =
    let sb = new StringBuilder()
    let rec build (node:HtmlNode) tabdepth =
        let tabs = String.init (tabdepth*4) (fun _ -> " ")
        if node.NodeType = HtmlNodeType.Text then
            if node.InnerText |> String.IsNullOrWhiteSpace |> not then sprintf """%srawText "%s" """ tabs node.InnerText |> sb.Append |> ignore
        else
            sb.Append tabs |> ignore
            sb.Append node.Name |> ignore
            sb.Append " [" |> ignore
            for i = 0 to node.Attributes.Count - 1 do 
                let attr = node.Attributes.[i] 
                sprintf """ attr "%s" "%s"; """ attr.Name attr.Value |> sb.Append |> ignore
            match node.ChildNodes.Count, node.Name with
            | 0,"area" | 0,"base" | 0,"br" | 0,"col" | 0,"command"
            | 0,"embed" | 0,"hr" | 0,"img" | 0,"input"
            | 0,"keygen" | 0,"link" | 0,"menuitem" | 0,"meta"
            | 0,"param" | 0,"source" | 0,"track" | 0,"wbr" -> sb.AppendLine "]" |> ignore
            | 0,_ -> sb.AppendLine "] []" |> ignore
            | _ ->
                sb.AppendLine "] [" |> ignore
                for i = 0 to node.ChildNodes.Count - 1 do
                    build node.ChildNodes.[i] <| tabdepth + 1
                sb.Append tabs |> ignore
                sb.AppendLine "]" |> ignore
    build head 0
    string sb

let doc = new HtmlDocument()
doc.Load """C:\Users\jtyso\Documents\Visual Studio 2017\Projects\Website\Website\public\experimental.html"""
printfn "%s" <| buildList doc.DocumentNode