module Types
open Suave.FunctionalViewEngine
open System
type Content = | Text of string | Nodes of (unit -> XmlNode list)
/// A website page
type Page = { 
    /// Title of the page
    Title: string; 
    /// Last modified timestamp
    Modified: DateTime; 
    /// Content to be rendered
    Content: Content }
let textify = renderHtmlNodes >> Text