"use client";

import { Sparkles, ArrowRight, Copy, Check, PenLine, Download } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

interface Step3Props {
    essay: any;
    onRestart: () => void;
}

export default function Step3Preview({ essay, onRestart }: Step3Props) {
    const [copied, setCopied] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    // Parse essay if it's a JSON string, or use as object
    const initialData = typeof essay === 'string' && essay.startsWith('{') ? JSON.parse(essay) : essay;

    const [essayData, setEssayData] = useState(initialData);

    const handleCopy = () => {
        const fullText = `${essayData.q1_motivation}\n\n${essayData.q2_academics}\n\n${essayData.q3_activities}`;
        navigator.clipboard.writeText(fullText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleDownload = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/download-docx`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    q1: essayData.q1_motivation,
                    q2: essayData.q2_academics,
                    q3: essayData.q3_activities
                })
            });

            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "My_Personal_Statement.docx";
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                alert("Failed to create Word doc");
            }
        } catch (e) {
            console.error(e);
            alert("Error downloading file");
        }
    };

    const updateField = (field: string, value: string) => {
        setEssayData((prev: any) => ({ ...prev, [field]: value }));
    };

    return (
        <div className="space-y-8 animate-in fade-in zoom-in-95 duration-500">
            <div className="text-center space-y-2">
                <div className="mx-auto h-12 w-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                    <Sparkles className="h-6 w-6" />
                </div>
                <h2 className="text-2xl font-serif font-bold text-gray-900">Your First Draft is Ready</h2>
                <p className="text-gray-500">The Phoenix Engine has structured your thoughts. Now the real writing begins.</p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
                <div className="bg-gray-50 border-b border-gray-200 px-6 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="h-3 w-3 bg-red-400 rounded-full" />
                        <span className="h-3 w-3 bg-yellow-400 rounded-full" />
                        <span className="h-3 w-3 bg-green-400 rounded-full" />
                    </div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setIsEditing(!isEditing)}
                            className={cn(
                                "text-xs flex items-center gap-1 transition-colors font-medium px-3 py-1.5 rounded-md",
                                isEditing ? "bg-teal-100 text-teal-700" : "text-gray-500 hover:text-gray-900 hover:bg-gray-100"
                            )}
                        >
                            <PenLine className="h-3 w-3" />
                            {isEditing ? "Editing Mode On" : "Edit Text"}
                        </button>
                        <button
                            onClick={handleCopy}
                            className="text-xs text-gray-500 hover:text-gray-900 flex items-center gap-1 transition-colors hover:bg-gray-100 px-3 py-1.5 rounded-md"
                        >
                            {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                            {copied ? "Copied" : "Copy All"}
                        </button>
                    </div>
                </div>

                <div className="p-8 max-h-[60vh] overflow-y-auto space-y-8 font-serif text-gray-800 leading-relaxed">
                    <section>
                        <h3 className="font-sans text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">1️⃣ Why do you want to study this course or subject?</h3>
                        {isEditing ? (
                            <textarea
                                className="w-full min-h-[150px] p-4 border border-teal-200 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none text-base"
                                value={essayData.q1_motivation}
                                onChange={(e) => updateField("q1_motivation", e.target.value)}
                            />
                        ) : (
                            <p className="whitespace-pre-wrap">{essayData.q1_motivation}</p>
                        )}
                    </section>
                    <div className="border-t border-gray-100" />
                    <section>
                        <h3 className="font-sans text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">2️⃣ How have your qualifications and studies prepared you for this course?</h3>
                        {isEditing ? (
                            <textarea
                                className="w-full min-h-[300px] p-4 border border-teal-200 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none text-base"
                                value={essayData.q2_academics}
                                onChange={(e) => updateField("q2_academics", e.target.value)}
                            />
                        ) : (
                            <p className="whitespace-pre-wrap">{essayData.q2_academics}</p>
                        )}
                    </section>
                    <div className="border-t border-gray-100" />
                    <section>
                        <h3 className="font-sans text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">3️⃣ What else have you done to prepare for this course?</h3>
                        {isEditing ? (
                            <textarea
                                className="w-full min-h-[400px] p-4 border border-teal-200 rounded-lg focus:ring-2 focus:ring-teal-500 outline-none text-base"
                                value={essayData.q3_activities}
                                onChange={(e) => updateField("q3_activities", e.target.value)}
                            />
                        ) : (
                            <p className="whitespace-pre-wrap">{essayData.q3_activities}</p>
                        )}
                    </section>
                </div>
            </div>

            <div className="flex justify-center gap-4">
                <button
                    onClick={onRestart}
                    className="px-6 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg font-medium transition-colors"
                >
                    Start Over
                </button>
                <button
                    className="px-6 py-2.5 bg-blue-900 hover:bg-blue-800 text-white rounded-lg font-medium shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                    onClick={handleDownload}
                >
                    Download for Word <Download className="h-4 w-4" />
                </button>
            </div>
        </div>
    );
}
