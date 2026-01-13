"use client";

import { MessageSquareQuote } from "lucide-react";

interface Step2Props {
    data: any;
    updateData: (key: string, value: any) => void;
}

export default function Step2Motivation({ data, updateData }: Step2Props) {
    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                    <div className="p-2 bg-rose-100 rounded-lg">
                        <MessageSquareQuote className="h-5 w-5 text-rose-600" />
                    </div>
                    <h2 className="text-xl font-serif font-bold text-gray-900">The Spark</h2>
                </div>

                <p className="text-gray-600 mb-6 text-sm">
                    Every great personal statement starts with a "Why". Use the box below to tell us about the moment you realized this subject was for you.
                    Don't worry about being formal—just get the story down.
                </p>

                <div className="relative">
                    <textarea
                        className="w-full p-6 border border-gray-300 rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-rose-500 outline-none transition-all h-96 resize-none text-lg leading-relaxed font-serif text-gray-800 bg-gray-50/50"
                        placeholder="It all started when..."
                        value={data.motivation}
                        onChange={(e) => updateData("motivation", e.target.value)}
                    />
                    <div className="absolute bottom-4 right-4 text-xs text-gray-400 font-medium">
                        {data.motivation.length} chars
                    </div>
                </div>
            </div>

            <div className="bg-teal-50 border border-teal-100 p-4 rounded-lg flex gap-3 text-sm text-teal-800">
                <span className="text-xl">💡</span>
                <p>
                    <strong>Tip:</strong> Avoid "I have always been passionate about...". Instead, show us a specific problem you tried to solve or a question you couldn't stop asking.
                </p>
            </div>
        </div>
    );
}
