/**
 * Accessibility Checker Component
 * Provides real-time accessibility analysis for content
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationTriangleIcon,
  InformationCircleIcon,
  DocumentTextIcon,
  PhotoIcon,
  VideoCameraIcon
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { useI18n } from '@/lib/i18n';

interface AccessibilityIssue {
  type: string;
  severity: string;
  message: string;
  suggestion: string;
  wcag_guideline?: string;
}

interface AccessibilityScore {
  overall_score: number;
  level: string;
  alt_text_score: number;
  contrast_score: number;
  text_readability_score: number;
  subtitle_score: number;
  issues: AccessibilityIssue[];
  recommendations: string[];
}

interface AccessibilityCheckerProps {
  content?: {
    title?: string;
    caption?: string;
    alt_text?: string;
    subtitles?: string;
  };
  onScoreChange?: (score: AccessibilityScore) => void;
  className?: string;
}

export function AccessibilityChecker({ content, onScoreChange, className }: AccessibilityCheckerProps) {
  const { t } = useI18n('content');
  const [score, setScore] = useState<AccessibilityScore | null>(null);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp'],
      'video/*': ['.mp4', '.avi', '.mov', '.wmv']
    },
    multiple: true
  });

  const checkAccessibility = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      
      // Add content data
      if (content?.title) formData.append('title', content.title);
      if (content?.caption) formData.append('caption', content.caption);
      if (content?.alt_text) formData.append('alt_text', content.alt_text);
      if (content?.subtitles) formData.append('subtitles', content.subtitles);
      
      // Add files
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('/api/v1/accessibility/check', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Accessibility check failed');
      }

      const result = await response.json();
      setScore(result);
      onScoreChange?.(result);
    } catch (error) {
      console.error('Accessibility check error:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const getScoreColor = (scoreValue: number) => {
    if (scoreValue >= 90) return 'text-green-600';
    if (scoreValue >= 75) return 'text-blue-600';
    if (scoreValue >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (scoreValue: number) => {
    if (scoreValue >= 90) return 'bg-green-50 border-green-200';
    if (scoreValue >= 75) return 'bg-blue-50 border-blue-200';
    if (scoreValue >= 50) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      case 'info':
        return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <div className={clsx("space-y-6", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          {t('accessibilityCheck')}
        </h3>
        <button
          onClick={checkAccessibility}
          disabled={loading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? (
            <>
              <div className="animate-spin -ml-1 mr-3 h-5 w-5 text-white">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </div>
              Checking...
            </>
          ) : (
            t('checkAccessibility')
          )}
        </button>
      </div>

      {/* File Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Media Files (Optional)
        </label>
        <div
          {...getRootProps()}
          className={clsx(
            "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
            isDragActive
              ? "border-blue-400 bg-blue-50 dark:bg-blue-900/20"
              : "border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500"
          )}
        >
          <input {...getInputProps()} />
          <div className="space-y-2">
            <div className="flex justify-center">
              <PhotoIcon className="h-12 w-12 text-gray-400" />
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {isDragActive ? (
                <p>Drop files here...</p>
              ) : (
                <p>
                  <span className="font-medium">Click to upload</span> or drag and drop
                  <br />
                  Images and videos for accessibility analysis
                </p>
              )}
            </div>
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-4 space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded-md"
              >
                <div className="flex items-center space-x-2">
                  {file.type.startsWith('image/') ? (
                    <PhotoIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <VideoCameraIcon className="h-5 w-5 text-gray-400" />
                  )}
                  <span className="text-sm text-gray-700 dark:text-gray-300">{file.name}</span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <XCircleIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Results */}
      {score && (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className={clsx(
            "p-6 border rounded-lg",
            getScoreBackground(score.overall_score)
          )}>
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                {t('accessibilityScore')}
              </h4>
              <div className={clsx(
                "text-2xl font-bold",
                getScoreColor(score.overall_score)
              )}>
                {score.overall_score.toFixed(1)}/100
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <div className={clsx("text-lg font-semibold", getScoreColor(score.alt_text_score))}>
                  {score.alt_text_score.toFixed(0)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Alt Text</div>
              </div>
              <div className="text-center">
                <div className={clsx("text-lg font-semibold", getScoreColor(score.contrast_score))}>
                  {score.contrast_score.toFixed(0)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Contrast</div>
              </div>
              <div className="text-center">
                <div className={clsx("text-lg font-semibold", getScoreColor(score.text_readability_score))}>
                  {score.text_readability_score.toFixed(0)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Readability</div>
              </div>
              <div className="text-center">
                <div className={clsx("text-lg font-semibold", getScoreColor(score.subtitle_score))}>
                  {score.subtitle_score.toFixed(0)}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Subtitles</div>
              </div>
            </div>

            <div className={clsx(
              "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium",
              score.level === 'excellent' && "bg-green-100 text-green-800",
              score.level === 'good' && "bg-blue-100 text-blue-800",
              score.level === 'needs_improvement' && "bg-yellow-100 text-yellow-800",
              score.level === 'poor' && "bg-red-100 text-red-800"
            )}>
              {score.level.replace('_', ' ').toUpperCase()}
            </div>
          </div>

          {/* Issues */}
          {score.issues.length > 0 && (
            <div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Issues Found
              </h4>
              <div className="space-y-3">
                {score.issues.map((issue, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
                  >
                    {getSeverityIcon(issue.severity)}
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {issue.message}
                        </span>
                        {issue.wcag_guideline && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                            WCAG {issue.wcag_guideline}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {issue.suggestion}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {score.recommendations.length > 0 && (
            <div>
              <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Recommendations
              </h4>
              <ul className="space-y-2">
                {score.recommendations.map((recommendation, index) => (
                  <li
                    key={index}
                    className="flex items-start space-x-3 text-sm text-gray-700 dark:text-gray-300"
                  >
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}