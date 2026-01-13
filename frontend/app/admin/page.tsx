"use client";

import { useState, useEffect } from "react";
import { Upload, Brain, CheckCircle, AlertCircle, Loader2, Play } from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

export default function AdminPage() {
    const [stats, setStats] = useState<{ essay_count: number } | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<string>("");
    const [analysisStatus, setAnalysisStatus] = useState<any>(null);

    // Fetch stats on load
    const fetchStats = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/stats`);
            if (res.ok) {
                const data = await res.json();
                setStats(data);
            }
        } catch (e) {
            console.error("Failed to fetch stats", e);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        setIsUploading(true);
        setUploadStatus("Uploading...");

        try {
            let successCount = 0;
            for (let i = 0; i < files.length; i++) {
                const formData = new FormData();
                formData.append("file", files[i]);

                const res = await fetch(`${API_BASE_URL}/ingest`, {
                    method: "POST",
                    body: formData,
                });

                if (res.ok) successCount++;
            }
            setUploadStatus(`Successfully uploaded ${successCount} files.`);
            fetchStats(); // Refresh stats
        } catch (err) {
            setUploadStatus("Error uploading files.");
        } finally {
            setIsUploading(false);
        }
    };

    const handleAnalyze = async () => {
        setIsAnalyzing(true);
        setAnalysisStatus(null);
        try {
            const res = await fetch(`${API_BASE_URL}/analyze`, {
                method: "POST"
            });
            const data = await res.json();
            setAnalysisStatus(data);
        } catch (err) {
            setAnalysisStatus({ error: "Failed to trigger analysis." });
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-serif font-bold text-gray-900">Brain Training Center</h1>
                    <p className="text-gray-500 mt-1">Upload successful essays to teach the AI what "good" looks like.</p>
                </div>
                <div className="bg-white px-4 py-2 rounded-lg border border-gray-200 shadow-sm flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    <span className="font-semibold text-gray-700">
                        Start Count: {stats ? stats.essay_count : "..."}
                    </span>
                </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
                {/* Upload Card */}
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Upload className="h-5 w-5 text-blue-600" /> Upload Exemplars
                    </h2>
                    <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 flex flex-col items-center justify-center text-center hover:bg-gray-50 transition-colors relative">
                        <input
                            type="file"
                            multiple
                            accept=".pdf,.docx"
                            onChange={handleFileUpload}
                            disabled={isUploading}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />
                        <div className="h-12 w-12 bg-blue-50 rounded-full flex items-center justify-center mb-3">
                            {isUploading ? <Loader2 className="h-6 w-6 text-blue-600 animate-spin" /> : <Upload className="h-6 w-6 text-blue-600" />}
                        </div>
                        <p className="font-medium text-gray-900">
                            {isUploading ? "Ingesting..." : "Drop PDFs or Word Docs here"}
                        </p>
                        <p className="text-sm text-gray-500 mt-1">or click to browse</p>
                    </div>
                    {uploadStatus && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-600 flex items-center gap-2">
                            <CheckCircle className="h-4 w-4 text-green-500" /> {uploadStatus}
                        </div>
                    )}
                </div>

                {/* Analyze Card */}
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Brain className="h-5 w-5 text-purple-600" /> Global Analysis
                    </h2>
                    <p className="text-gray-600 text-sm mb-6">
                        After uploading, you must run an analysis so the AI can learn the structure and style patterns of the new essays.
                    </p>

                    <button
                        onClick={handleAnalyze}
                        disabled={isAnalyzing}
                        className={cn(
                            "w-full py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-all",
                            isAnalyzing
                                ? "bg-purple-100 text-purple-700"
                                : "bg-purple-600 text-white hover:bg-purple-700 shadow-md hover:shadow-lg"
                        )}
                    >
                        {isAnalyzing ? (
                            <><Loader2 className="h-4 w-4 animate-spin" /> Analyzing Corpus...</>
                        ) : (
                            <><Play className="h-4 w-4" /> Run Deep Learning Analysis</>
                        )}
                    </button>

                    {analysisStatus && (
                        <div className="mt-6 space-y-2 text-sm">
                            {analysisStatus.error ? (
                                <div className="p-3 bg-red-50 text-red-700 rounded-lg flex gap-2">
                                    <AlertCircle className="h-4 w-4" /> {analysisStatus.error}
                                </div>
                            ) : (
                                <div className="p-4 bg-green-50 border border-green-100 rounded-lg space-y-2">
                                    <h3 className="font-bold text-green-800 flex items-center gap-2">
                                        <CheckCircle className="h-4 w-4" /> Blueprint Updated!
                                    </h3>
                                    {analysisStatus.Structure_Blueprint && (
                                        <div className="grid grid-cols-3 gap-2 mt-2">
                                            <div className="bg-white p-2 rounded text-center shadow-sm">
                                                <div className="text-xs text-gray-500">Q1</div>
                                                <div className="font-bold">{analysisStatus.Structure_Blueprint.Q1_percentage}%</div>
                                            </div>
                                            <div className="bg-white p-2 rounded text-center shadow-sm">
                                                <div className="text-xs text-gray-500">Q2</div>
                                                <div className="font-bold">{analysisStatus.Structure_Blueprint.Q2_percentage}%</div>
                                            </div>
                                            <div className="bg-white p-2 rounded text-center shadow-sm">
                                                <div className="text-xs text-gray-500">Q3</div>
                                                <div className="font-bold">{analysisStatus.Structure_Blueprint.Q3_percentage}%</div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
