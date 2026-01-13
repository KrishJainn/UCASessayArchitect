"use client";

import { Upload, FileText, CheckCircle, Loader2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

interface Step1Props {
    data: any;
    updateData: (key: string, value: any) => void;
}

export default function Step1Profile({ data, updateData }: Step1Props) {
    const [isUploading, setIsUploading] = useState(false);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            // Use full URL for safety, or setup proxy. Using localhost:8000 for now.
            const res = await fetch(`${API_BASE_URL}/parse-cv`, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Upload failed");

            const json = await res.json();
            updateData("cv_text", json.text);
            updateData("cv_filename", file.name);
        } catch (err) {
            console.error(err);
            alert("Failed to parse CV");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h2 className="text-xl font-serif font-bold text-gray-900 mb-4">Essay Generator</h2>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Target Course</label>
                        <input
                            type="text"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                            placeholder="e.g. Computer Science, Law, Economics"
                            value={data.target_course}
                            onChange={(e) => updateData("target_course", e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Super-Curriculars</label>
                        <p className="text-xs text-gray-500 mb-2">Books read, lectures watched, courses taken (outside of school).</p>
                        <textarea
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all h-24 resize-none"
                            placeholder="e.g. Read 'Thinking, Fast and Slow', Completed CS50..."
                            value={data.super_curriculars}
                            onChange={(e) => updateData("super_curriculars", e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Work Experience / Skills</label>
                        <textarea
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all h-20 resize-none"
                            placeholder="e.g. Python styling, Debate Team Captain..."
                            value={data.work_experience}
                            onChange={(e) => updateData("work_experience", e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="bg-blue-50 border border-blue-100 p-6 rounded-xl">
                <div className="flex items-start justify-between">
                    <div>
                        <h3 className="font-semibold text-blue-900 flex items-center gap-2">
                            <FileText className="h-4 w-4" />
                            {data.cv_filename ? "CV Uploaded" : "Upload CV / Resume"}
                        </h3>
                        <p className="text-sm text-blue-700 mt-1 max-w-md">
                            We'll extract your achievements, awards, and dates to make the essay hyper-specific.
                        </p>
                        {data.cv_filename && (
                            <div className="mt-2 text-xs font-mono text-green-700 bg-green-100 px-2 py-1 rounded inline-flex items-center gap-1">
                                <CheckCircle className="h-3 w-3" /> {data.cv_filename}
                            </div>
                        )}
                    </div>

                    <label className={cn(
                        "cursor-pointer flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all text-sm",
                        isUploading
                            ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                            : "bg-white text-blue-700 hover:bg-blue-100 border border-blue-200 shadow-sm"
                    )}>
                        {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                        {isUploading ? "Parsing..." : (data.cv_filename ? "Replace File" : "Choose File")}
                        <input type="file" className="hidden" accept=".pdf,.docx" onChange={handleFileUpload} disabled={isUploading} />
                    </label>
                </div>
            </div>
        </div>
    );
}
