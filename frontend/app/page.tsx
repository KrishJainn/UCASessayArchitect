"use client";

import Link from "next/link";
import { Plus, ArrowRight, FileText, Clock } from "lucide-react";

export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif font-bold text-gray-900">Welcome back, Student</h1>
          <p className="text-gray-500 mt-1">Ready to craft your next masterpiece?</p>
        </div>
        <Link
          href="/new"
          className="flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-sm"
        >
          <Plus className="h-5 w-5" />
          Essay Generator
        </Link>
      </div>

      {/* Recent Work */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Project Card Suggestion */}
        <div className="group border border-gray-200 bg-white rounded-xl p-6 hover:shadow-md transition-all cursor-pointer relative overflow-hidden">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-rose-50 rounded-lg group-hover:bg-rose-100 transition-colors">
              <FileText className="h-6 w-6 text-rose-700" />
            </div>
            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">Draft</span>
          </div>
          <h3 className="font-serif text-lg font-bold text-gray-900 mb-1">Computer Science Personal Statement</h3>
          <p className="text-sm text-gray-500 line-clamp-2">My interest in algorithms began when I observed the traffic patterns...</p>

          <div className="mt-4 flex items-center justify-between pt-4 border-t border-gray-50 text-xs text-gray-400">
            <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> 2h ago</span>
            <span className="group-hover:translate-x-1 transition-transform text-rose-600 font-medium flex items-center gap-1">Open <ArrowRight className="h-3 w-3" /></span>
          </div>
        </div>

        {/* Empty State / Create New */}
        <Link href="/new" className="border-2 border-dashed border-gray-200 rounded-xl p-6 flex flex-col items-center justify-center text-center hover:border-rose-300 hover:bg-rose-50/50 transition-all group">
          <div className="h-12 w-12 bg-gray-50 rounded-full flex items-center justify-center mb-3 group-hover:bg-white group-hover:shadow-sm">
            <Plus className="h-6 w-6 text-gray-400 group-hover:text-rose-500" />
          </div>
          <h3 className="font-medium text-gray-900">Start New Essay</h3>
          <p className="text-sm text-gray-500 mt-1">Generate a new SOP draft</p>
        </Link>
      </div>
    </div>
  );
}
