{-# LANGUAGE ExtendedDefaultRules, OverloadedStrings, QuasiQuotes, TemplateHaskell, TypeFamilies #-}

module HelloWorld where

import Yesod
import Text.Hamlet (HtmlUrl, hamlet)
import Text.Lucius (CssUrl, renderCss, Css)
import Text.Blaze.Html.Renderer.String (renderHtml)
import Data.Char (toLower)
import Data.Time (getCurrentTime)
import Data.List (sort)
import Data.Text (Text, append, pack)
import Data.Text.Internal.Lazy (Text)
import Control.Arrow
import Network.HTTP.Types (renderQueryText)
import Data.Text.Encoding (decodeUtf8)
import Blaze.ByteString.Builder (toByteString)

data Person = Person {
    name :: String
    ,age :: Int
}
data App = App

mkYesod "App" [parseRoutes|
/ HomeR GET
/myPath MyPathR GET 
/style.css StyleR GET
|] 

myLayout :: Widget -> Handler Html
myLayout widget = do
    mmsg <- getMessage
    pc <- widgetToPageContent $ do
        widget
        toWidget [lucius| body {font-family: verdana}|]
    withUrlRenderer [hamlet|
    $doctype 5
    <html>
        <head>
            <title>#{pageTitle pc}
            <meta charset=utf-8>
            ^{pageHead pc}
        <body>
            <article>
                $maybe msg <- mmsg
                    <div #message>#{msg}
                ^{pageBody pc}
    |]

instance Yesod App where 
    defaultLayout = myLayout

getStyleR :: Handler Css
getStyleR = do
    render <- getUrlRenderParams 
    return $ [lucius|
        .pone {
            font-weight: bold;
            color: red;
            background-color: green;
        }
        h1 {
            color: blue;
        }
    |] undefined

getHomeR :: HandlerT App IO Value
getHomeR = return $ object ["msg" .= "Hello World"]

-- name :: [Char] -> [Char]
-- name = ("My Name is " ++)

getMyPathR :: Handler Html
getMyPathR = defaultLayout $ do
    now <- liftIO getCurrentTime
    setMessage $ toHtml $ "You previously visited at: " ++ show now
    let peeps = [Person "James" 22, Person "Kate" 17]
    let curPage = 2
    let person = Person "Jon" 27
    let lt = curPage - 1 <= 0
    setTitle "My Page"
    addScriptRemote "https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"
    addStylesheet StyleR
    -- toWidgetHead [hamlet|
    --     <link rel=stylesheet type=text/css href=@{StyleR}>
    --     |]
    toWidget [julius|
    $(() =>{
        $("h1").click(() => alert("You clicked on the heading!"));
    });
    |]
    [whamlet|
        <h1>Bang!
        <p>Hello, my name s #{name person} and I am #{show $ age person}.
        <p .pone>
            Let's do some funny stuff with my name: #
            <b>#{sort $ map toLower (name person)}
        <p>Oh, and in 5 years I'll be #{show ((+) 5 (age person))} years old.
        <ul>
            $forall person <- peeps
                <li>
                    <span>#{name person}
                    <span>#{age person}
        <p>You are currently on page #{curPage}.
        ^{footer}
    |] 
    -- <a href=@?{(SomePage, [("page", pack $ show $ curPage - 1)])}>
    -- $if lt
    --     Previous
    -- $else
    --     First
    -- <a href=@?{(SomePage, [("page", pack $ show $ curPage + 1)])}>Next

footer :: Widget
footer = [whamlet|
<footer>
    Return to #
    <a href=@{HomeR}>Homepage
    \.
|] 

main :: IO ()
main = warp 3000 App