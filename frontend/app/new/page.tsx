"use client";

import { useState } from "react";
import { ArrowLeft, ArrowRight, Loader2, Sparkles } from "lucide-react";
import Step1Profile from "@/app/components/wizard/Step1Profile";
import Step2Motivation from "@/app/components/wizard/Step2Motivation";
import Step3Preview from "@/app/components/wizard/Step3Preview";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

export default function NewEssayWizard() {
    const [step, setStep] = useState(1);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedEssay, setGeneratedEssay] = useState<any>(null);

    const [formData, setFormData] = useState({
        target_course: "",
        super_curriculars: "",
        work_experience: "",
        motivation: "",
        cv_text: "",
        cv_filename: ""
    });

    const updateData = (key: string, value: any) => {
        setFormData(prev => ({ ...prev, [key]: value }));
    };

    const handleNext = async () => {
        if (step === 2) {
            // Generate
            setIsGenerating(true);
            try {
                const res = await fetch("http://localhost:8000/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ profile: formData })
                });

                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Generation failed");
                }

                const data = await res.json();
                setGeneratedEssay(data);
                setStep(3);
            } catch (e: any) {
                alert("Error generating essay: " + e.message);
            } finally {
                setIsGenerating(false);
            }
        } else {
            setStep(prev => prev + 1);
        }
    };

    const handleBack = () => {
        setStep(prev => prev - 1);
    };

    // Loading State
    if (isGenerating) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6 animate-in fade-in duration-500">
                <div className="relative">
                    <div className="absolute inset-0 bg-rose-500 blur-xl opacity-20 animate-pulse rounded-full"></div>
                    <Loader2 className="h-16 w-16 text-rose-600 animate-spin relative z-10" />
                </div>
                <div>
                    <h3 className="text-xl font-serif font-bold text-gray-900">Consulting the Oracle...</h3>
                    <p className="text-gray-500 mt-2 max-w-sm mx-auto">
                        Analyzing {formData.target_course} admissions patterns and structuring your narrative.
                    </p>
                </div>
            </div>
        );
    }

    // Final Result State
    if (step === 3 && generatedEssay) {
        return <Step3Preview essay={generatedEssay} onRestart={() => setStep(1)} />;
    }

    return (
        <div className="max-w-3xl mx-auto pb-20">
            {/* Progress Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between text-sm font-medium text-gray-500 mb-2">
                    <span>Step {step} of 2</span>
                    <span>{Math.round((step / 2) * 100)}%</span>
                </div>
                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-rose-600 transition-all duration-500 ease-out"
                        style={{ width: `${(step / 2) * 100}%` }}
                    />
                </div>
            </div>

            {/* Dynamic Step Component */}
            <div className="min-h-[400px]">
                {step === 1 && <Step1Profile data={formData} updateData={updateData} />}
                {step === 2 && <Step2Motivation data={formData} updateData={updateData} />}
            </div>

            {/* Navigation Footer */}
            <div className="fixed bottom-0 left-64 right-0 p-4 bg-white border-t border-gray-200 flex items-center justify-between z-30">
                <div className="max-w-3xl mx-auto w-full flex justify-between px-8">
                    <button
                        onClick={handleBack}
                        disabled={step === 1}
                        className={cn(
                            "flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-colors",
                            step === 1
                                ? "text-gray-300 cursor-not-allowed"
                                : "text-gray-600 hover:bg-gray-100"
                        )}
                    >
                        <ArrowLeft className="h-4 w-4" /> Back
                    </button>

                    <button
                        onClick={handleNext}
                        disabled={
                            (step === 1 && !formData.target_course)
                        }
                        className={cn(
                            "flex items-center gap-2 px-8 py-2.5 rounded-lg font-semibold shadow-lg transition-all",
                            "bg-rose-900 text-white hover:bg-rose-800 hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                        )}
                    >
                        {step === 2 ? (
                            <>Generate Draft <Sparkles className="h-4 w-4" /></>
                        ) : (
                            <>Next Step <ArrowRight className="h-4 w-4" /></>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
