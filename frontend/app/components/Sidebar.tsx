"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, PenTool, Brain, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

const Sidebar = () => {
    const pathname = usePathname();
    const [essayCount, setEssayCount] = useState<number | null>(null);

    useEffect(() => {
        fetch(`${API_BASE_URL}/stats`)
            .then(res => res.json())
            .then(data => setEssayCount(data.essay_count))
            .catch(err => console.error(err));
    }, []);

    const links = [
        { href: "/", label: "Dashboard", icon: LayoutDashboard },
        { href: "/new", label: "Essay Generator", icon: PenTool },
        { href: "/admin", label: "Train AI", icon: Brain },
    ];

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-gray-200 bg-white shadow-sm flex flex-col justify-between">
            <div>
                <div className="flex flex-col items-center justify-center py-8 border-b border-gray-100 gap-3">
                    <img src="/logo.png" alt="InfoyoungIndia" className="h-24 w-auto object-contain" />
                    <span className="text-xl font-serif font-bold text-gray-900 tracking-tight">Infoyoung<span className="text-teal-600">India</span></span>
                </div>

                <div className="py-6 px-3 flex flex-col gap-1">
                    {links.map((link) => {
                        const isActive = pathname === link.href || (pathname.startsWith(link.href) && link.href !== "/");
                        const Icon = link.icon;
                        return (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                                    isActive
                                        ? "bg-rose-50 text-rose-700 shadow-sm ring-1 ring-rose-100"
                                        : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                )}
                            >
                                <Icon className={cn("h-5 w-5", isActive ? "text-rose-700" : "text-gray-400")} />
                                {link.label}
                            </Link>
                        )
                    })}
                </div>
            </div>

            <div className="p-6">
                <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                        <Zap className="h-3 w-3 text-teal-600" /> Brain Strength
                    </p>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-bold text-gray-800">
                            {essayCount !== null ? `${essayCount} Chunks` : "Loading..."}
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                        <div
                            className="bg-teal-600 h-1.5 rounded-full transition-all duration-1000"
                            style={{ width: `${Math.min((essayCount || 0) * 2, 100)}%` }} // Arbitrary progress visualization
                        ></div>
                    </div>
                    <p className="text-[10px] text-gray-500 mt-2">Trained on successful essays</p>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
