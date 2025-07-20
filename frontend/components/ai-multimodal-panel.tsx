"use client"

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  VideoIcon, 
  MicIcon, 
  ImageIcon, 
  SparklesIcon,
  PlayIcon,
  DownloadIcon 
} from 'lucide-react'

interface AIMultiModalPanelProps {
  className?: string
}

export function AIMultiModalPanel({ className }: AIMultiModalPanelProps) {
  const [activeFeature, setActiveFeature] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const features = [
    {
      id: 'ai-voiceover',
      title: 'AI Voiceover & Dubbing',
      description: 'Generate professional voiceovers and dub videos in multiple languages',
      icon: MicIcon,
      capabilities: [
        'Multi-language synthesis',
        'Voice cloning',
        'Podcast narration',
        'Real-time dubbing'
      ]
    },
    {
      id: 'image-to-video',
      title: 'Image to Video Generation',
      description: 'Transform static images into dynamic videos with AI-powered motion',
      icon: VideoIcon,
      capabilities: [
        'Motion effects',
        'Parallax videos',
        'Slideshow creation',
        'Text-to-video'
      ]
    },
    {
      id: 'enhanced-memes',
      title: 'AI Meme Generator',
      description: 'Create trending, brand-relevant memes with viral potential analysis',
      icon: SparklesIcon,
      capabilities: [
        'Trending format detection',
        'Brand alignment',
        'Viral score prediction',
        'Reactive memes'
      ]
    },
    {
      id: 'short-form-video',
      title: 'Short-Form Video Editing',
      description: 'AI-powered editing for Reels, TikTok, and YouTube Shorts',
      icon: PlayIcon,
      capabilities: [
        'Trend-based creation',
        'Hook optimization',
        'Educational content',
        'Product showcases'
      ]
    }
  ]

  const handleFeatureDemo = async (featureId: string) => {
    setIsProcessing(true)
    setActiveFeature(featureId)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setIsProcessing(false)
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold gradient-text">
          Multi-Modal AI Content Generation
        </h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Advanced AI-powered features for creating engaging social media content across all platforms
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon
          const isActive = activeFeature === feature.id
          
          return (
            <Card key={feature.id} className={`transition-all duration-300 hover:shadow-lg ${
              isActive ? 'ring-2 ring-primary' : ''
            }`}>
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {feature.capabilities.map((capability) => (
                    <Badge key={capability} variant="secondary" className="text-xs">
                      {capability}
                    </Badge>
                  ))}
                </div>
                
                <Button 
                  onClick={() => handleFeatureDemo(feature.id)}
                  disabled={isProcessing}
                  className="w-full"
                  variant={isActive ? "default" : "outline"}
                >
                  {isProcessing && isActive ? (
                    <>
                      <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-4 w-4 mr-2" />
                      Try Demo
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Feature Demo Section */}
      {activeFeature && !isProcessing && (
        <Card className="bg-gradient-to-r from-primary/5 to-secondary/5">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <SparklesIcon className="h-5 w-5" />
              <span>AI Feature Demo Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-background rounded-lg border">
                <h4 className="font-semibold mb-2">Generated Content Preview</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="w-full h-32 bg-muted rounded-lg flex items-center justify-center">
                      <VideoIcon className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <p className="text-sm text-center">Video Output</p>
                  </div>
                  <div className="space-y-2">
                    <div className="w-full h-32 bg-muted rounded-lg flex items-center justify-center">
                      <MicIcon className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <p className="text-sm text-center">Audio Track</p>
                  </div>
                  <div className="space-y-2">
                    <div className="w-full h-32 bg-muted rounded-lg flex items-center justify-center">
                      <ImageIcon className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <p className="text-sm text-center">Thumbnails</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div>
                  <p className="font-semibold text-green-700 dark:text-green-300">
                    Content Generated Successfully!
                  </p>
                  <p className="text-sm text-green-600 dark:text-green-400">
                    Viral Score: 8.5/10 • Platform Optimized • Ready to Publish
                  </p>
                </div>
                <Button size="sm" className="bg-green-600 hover:bg-green-700">
                  <DownloadIcon className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* API Integration Examples */}
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="text-lg">API Integration Examples</CardTitle>
          <CardDescription>
            Ready-to-use API endpoints for developers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <h4 className="font-semibold">AI Voiceover</h4>
                <code className="block p-2 bg-muted rounded text-xs">
                  POST /api/v1/ai-multimodal/ai-voiceover/generate
                </code>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Image to Video</h4>
                <code className="block p-2 bg-muted rounded text-xs">
                  POST /api/v1/ai-multimodal/image-to-video/create
                </code>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Enhanced Memes</h4>
                <code className="block p-2 bg-muted rounded text-xs">
                  POST /api/v1/ai-multimodal/enhanced-memes/trending
                </code>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold">Short-Form Video</h4>
                <code className="block p-2 bg-muted rounded text-xs">
                  POST /api/v1/ai-multimodal/short-form-video/create
                </code>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AIMultiModalPanel