import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
    const [files, setFiles] = useState([]);
    const [currentFile, setCurrentFile] = useState('');
    const [code, setCode] = useState('');
    const [instruction, setInstruction] = useState('');
    const [response, setResponse] = useState('');
    const [agentInstruction, setAgentInstruction] = useState('');
    const [agentTasks, setAgentTasks] = useState([]);

    useEffect(() => {
        fetchFiles();
    }, []);

    const fetchFiles = async () => {
        try {
            const res = await axios.get(`${API_URL}/files`);
            setFiles(res.data.files);
        } catch (error) {
            console.error('Error fetching files:', error);
        }
    };

    const fetchFileContent = async (filename) => {
        try {
            const res = await axios.get(`${API_URL}/files/${filename}`);
            setCode(res.data.content);
            setCurrentFile(filename);
        } catch (error) {
            console.error('Error fetching file content:', error);
        }
    };

    const saveFile = async () => {
        try {
            await axios.post(`${API_URL}/files/${currentFile}`, { content: code });
            alert('File saved successfully!');
        } catch (error) {
            console.error('Error saving file:', error);
        }
    };

    const handleEdit = async () => {
        try {
            const res = await axios.post(`${API_URL}/edit`, { content: code, instruction });
            setResponse(res.data.response);
            setCode(res.data.response); // Automatically update the editor with the new code
        } catch (error) {
            console.error('Error editing code:', error);
        }
    };

    const createNewFile = async () => {
        const newFileName = prompt("Enter the new file name:");
        if (newFileName) {
            try {
                await axios.post(`${API_URL}/files/${newFileName}`, { content: '' });
                fetchFiles();
                setCurrentFile(newFileName);
                setCode('');
            } catch (error) {
                console.error('Error creating new file:', error);
            }
        }
    };

    const handleAgentExecute = async () => {
        try {
            const res = await axios.post(`${API_URL}/agent/execute`, { instruction: agentInstruction });
            setAgentTasks(res.data.tasks);
        } catch (error) {
            console.error('Error executing agent instruction:', error);
        }
    };

    return (
        <div className="App">
            <div className="sidebar">
                <h2>Files</h2>
                <button onClick={createNewFile}>New File</button>
                <ul>
                    {files.map((file) => (
                        <li key={file} onClick={() => fetchFileContent(file)}>
                            {file}
                        </li>
                    ))}
                </ul>
            </div>
            <div className="main-content">
                <div className="editor-container">
                    <Editor
                        height="80vh"
                        language="python"
                        value={code}
                        onChange={(value) => setCode(value)}
                    />
                    <button onClick={saveFile} disabled={!currentFile}>Save File</button>
                </div>
                <div className="chat-panel">
                    <h2>Chat</h2>
                    <textarea
                        value={instruction}
                        onChange={(e) => setInstruction(e.target.value)}
                        placeholder="Enter instruction for selected file..."
                    />
                    <button onClick={handleEdit}>Apply Instruction</button>
                    {response && (
                        <div className="response">
                            <h3>LLM Response:</h3>
                            <pre>{response}</pre>
                        </div>
                    )}
                </div>
                <div className="agent-panel">
                    <h2>Agent Mode</h2>
                    <textarea
                        value={agentInstruction}
                        onChange={(e) => setAgentInstruction(e.target.value)}
                        placeholder="Enter high-level instruction for the agent..."
                    />
                    <button onClick={handleAgentExecute}>Execute</button>
                    {agentTasks.length > 0 && (
                        <div className="tasks">
                            <h3>Agent Tasks:</h3>
                            <ul>
                                {agentTasks.map((task, index) => (
                                    <li key={index}>
                                        <strong>{task.action}:</strong> {JSON.stringify(task.args)}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default App;
