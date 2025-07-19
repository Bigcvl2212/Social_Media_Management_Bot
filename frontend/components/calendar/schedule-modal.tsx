"use client";

import { Fragment, useState } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { XMarkIcon, PhotoIcon, CalendarIcon } from "@heroicons/react/24/outline";
import { format } from "date-fns";

interface ScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedDate: Date | null;
}

const platforms = [
  { id: "instagram", name: "Instagram", icon: "IG", color: "from-purple-500 to-pink-500" },
  { id: "tiktok", name: "TikTok", icon: "TT", color: "from-gray-800 to-black" },
  { id: "youtube", name: "YouTube", icon: "YT", color: "from-red-600 to-red-700" },
  { id: "twitter", name: "X (Twitter)", icon: "X", color: "from-gray-800 to-black" },
  { id: "facebook", name: "Facebook", icon: "FB", color: "from-blue-600 to-blue-700" },
  { id: "linkedin", name: "LinkedIn", icon: "LI", color: "from-blue-700 to-blue-800" },
];

export function ScheduleModal({ isOpen, onClose, selectedDate }: ScheduleModalProps) {
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    platforms: [] as string[],
    scheduledDate: selectedDate ? format(selectedDate, "yyyy-MM-dd") : "",
    scheduledTime: "09:00",
    imageFile: null as File | null,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement actual scheduling logic
    console.log("Scheduling post:", formData);
    onClose();
    // Reset form
    setFormData({
      title: "",
      content: "",
      platforms: [],
      scheduledDate: selectedDate ? format(selectedDate, "yyyy-MM-dd") : "",
      scheduledTime: "09:00",
      imageFile: null,
    });
  };

  const handlePlatformToggle = (platformId: string) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId]
    }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData(prev => ({ ...prev, imageFile: file }));
    }
  };

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-xl glass-strong text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl border border-white/10">
                <form onSubmit={handleSubmit}>
                  {/* Header */}
                  <div className="flex items-center justify-between p-6 border-b border-white/10">
                    <div>
                      <Dialog.Title className="text-lg font-semibold text-white">
                        Schedule New Post
                      </Dialog.Title>
                      {selectedDate && (
                        <p className="text-sm text-gray-400 mt-1">
                          {format(selectedDate, "EEEE, MMMM d, yyyy")}
                        </p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={onClose}
                      className="rounded-lg glass-strong p-2 hover:bg-white/20 transition-colors"
                    >
                      <XMarkIcon className="h-5 w-5 text-gray-300" />
                    </button>
                  </div>

                  {/* Form Content */}
                  <div className="p-6 space-y-6">
                    {/* Title */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Post Title
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.title}
                        onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                        className="w-full glass-strong rounded-lg border border-white/10 px-4 py-2 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Enter a descriptive title for your post"
                      />
                    </div>

                    {/* Content */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Content
                      </label>
                      <textarea
                        required
                        rows={4}
                        value={formData.content}
                        onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                        className="w-full glass-strong rounded-lg border border-white/10 px-4 py-2 text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        placeholder="Write your post content here..."
                      />
                      <p className="text-xs text-gray-400 mt-1">
                        {formData.content.length}/280 characters
                      </p>
                    </div>

                    {/* Platforms */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-3">
                        Select Platforms
                      </label>
                      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                        {platforms.map((platform) => (
                          <button
                            key={platform.id}
                            type="button"
                            onClick={() => handlePlatformToggle(platform.id)}
                            className={`p-3 rounded-lg border transition-all ${
                              formData.platforms.includes(platform.id)
                                ? 'border-blue-500 bg-blue-500/20 glass-strong'
                                : 'border-white/10 glass hover:bg-white/5'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${platform.color} flex items-center justify-center text-white text-xs font-bold`}>
                                {platform.icon}
                              </div>
                              <span className="text-sm text-white font-medium">
                                {platform.name}
                              </span>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Date and Time */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Date
                        </label>
                        <div className="relative">
                          <input
                            type="date"
                            required
                            value={formData.scheduledDate}
                            onChange={(e) => setFormData(prev => ({ ...prev, scheduledDate: e.target.value }))}
                            className="w-full glass-strong rounded-lg border border-white/10 px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                          <CalendarIcon className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none" />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Time
                        </label>
                        <input
                          type="time"
                          required
                          value={formData.scheduledTime}
                          onChange={(e) => setFormData(prev => ({ ...prev, scheduledTime: e.target.value }))}
                          className="w-full glass-strong rounded-lg border border-white/10 px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    {/* Image Upload */}
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Media (Optional)
                      </label>
                      <div className="border-2 border-dashed border-white/20 rounded-lg p-6 text-center glass">
                        <input
                          type="file"
                          accept="image/*,video/*"
                          onChange={handleImageChange}
                          className="hidden"
                          id="media-upload"
                        />
                        <label htmlFor="media-upload" className="cursor-pointer">
                          <PhotoIcon className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                          <p className="text-sm text-gray-300 mb-1">
                            {formData.imageFile ? formData.imageFile.name : "Click to upload media"}
                          </p>
                          <p className="text-xs text-gray-400">
                            PNG, JPG, GIF, MP4 up to 100MB
                          </p>
                        </label>
                      </div>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-end gap-3 p-6 border-t border-white/10">
                    <button
                      type="button"
                      onClick={onClose}
                      className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={formData.platforms.length === 0}
                      className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-medium rounded-lg hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Schedule Post
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}