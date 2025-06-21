import {BrowserRouter, Route, Routes} from 'react-router-dom'
import HomePage from './pages/HomePage.tsx'
import StoriesControl from './pages/StoriesControlPage.tsx'
import PostsControl from './pages/PostsControlPage.tsx'
import PostDetailsPage from "./pages/PostDetailsPage";
import StoryDetailsPage from "./pages/StoryDetailsPage";
import AccountsControlPage from "./pages/AccountsControlPage";
// import AssistantControl from './pages/AssistantControlPage.tsx'
import eruda from 'eruda';
import {AuthProvider} from './contexts/auth.tsx';
import BackButtonManager from "./components/BackButtonManager";
import {useEffect, useState} from "react";
import {type Emoji, listEmojis} from "./services/api";
import {expandViewport, init, mountViewport} from '@telegram-apps/sdk';
import PostTemplatesPage from "./pages/PostTemplatesPage";
import ChatTypesControlPage from "./pages/ChatTypesControlPage";


export default function App() {
    eruda.init();
    const [emojis, setEmojis] = useState<Emoji[]>([])

    useEffect(() => {
        listEmojis()
            .then(setEmojis);

        init();
        console.log("telegram initialized")

        if (mountViewport.isAvailable()) {
            mountViewport()
                .then(() => {
                    if (expandViewport.isAvailable()) {
                        expandViewport();
                    }
                })
                .catch(console.error);
        }
    }, [])

    return (
        <AuthProvider>
            <BrowserRouter>
                <BackButtonManager/>
                <Routes>
                    <Route path="/" element={<HomePage/>}/>
                    <Route path="/stories" element={<StoriesControl/>}/>
                    <Route path="/story-details" element={<StoryDetailsPage/>}/>
                    <Route path="/posts" element={<PostsControl emojis={emojis}/>}/>
                    <Route path="/post-details/:postToPublishId" element={<PostDetailsPage emojis={emojis}/>}/>
                    <Route path="/accounts" element={<AccountsControlPage/>}/>
                    <Route path="/posts/templates" element={<PostTemplatesPage />} />
                    <Route path="/chats" element={<ChatTypesControlPage />} />
                    {/*<Route path="/assistant" element={<AssistantControl />} />*/}
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    )
}
