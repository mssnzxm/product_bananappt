import React, { useState } from 'react';
import { Video, Upload, Play, Clock, X, CheckCircle, AlertTriangle } from 'lucide-react';
import { Button, Card, Textarea, useToast, Loading } from '@/components/shared';
import { apiClient } from '@/api/client';
import type { ApiResponse } from '@/types';

interface VideoAnalysisRequest {
  file: File;
  prompt?: string;
}

interface VideoAnalysisResponse {
  analysis: string;
  file_id: string;
  status: string;
}

interface VideoAnalysisStatus {
  status: 'UPLOADING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  message: string;
  progress?: number;
}

export const VideoAnalysis: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysisPrompt, setAnalysisPrompt] = useState('请详细分析这个视频的内容');
  const [analysisResult, setAnalysisResult] = useState<string>('');
  const [status, setStatus] = useState<VideoAnalysisStatus>({
    status: 'UPLOADING',
    message: '选择视频文件开始分析'
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // 检查文件大小（200MB限制）
      const maxSize = 200 * 1024 * 1024;
      if (file.size > maxSize) {
        show({ 
          message: `文件过大：${(file.size / 1024 / 1024).toFixed(1)}MB，最大支持 200MB`, 
          type: 'error' 
        });
        return;
      }
      
      // 检查文件类型
      if (!file.type.startsWith('video/')) {
        show({ message: '请选择视频文件', type: 'error' });
        return;
      }
      
      setSelectedFile(file);
      setStatus({
        status: 'UPLOADING',
        message: `已选择文件：${file.name}`
      });
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setStatus({
      status: 'UPLOADING',
      message: '选择视频文件开始分析'
    });
    setAnalysisResult('');
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      show({ message: '请先选择视频文件', type: 'error' });
      return;
    }

    setIsAnalyzing(true);
    setStatus({
      status: 'UPLOADING',
      message: '正在上传视频文件...',
      progress: 0
    });

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('prompt', analysisPrompt);

      // 上传并分析视频
      const response = await apiClient.post<ApiResponse<VideoAnalysisResponse>>('/api/video-analysis', formData, {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setStatus(prev => ({
              ...prev,
              progress
            }));
          }
        }
      });

      if (response.data.data) {
        setAnalysisResult(response.data.data.analysis);
        setStatus({
          status: 'COMPLETED',
          message: '视频分析完成'
        });
        show({ message: '视频分析完成', type: 'success' });
      }
    } catch (error: any) {
      console.error('视频分析失败:', error);
      setStatus({
        status: 'FAILED',
        message: `分析失败：${error?.response?.data?.error?.message || error.message || '未知错误'}`
      });
      show({ 
        message: `视频分析失败: ${error?.response?.data?.error?.message || error.message || '未知错误'}`, 
        type: 'error' 
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'UPLOADING':
        return <Upload size={24} className="text-blue-500" />;
      case 'PROCESSING':
        return <Clock size={24} className="text-yellow-500" />;
      case 'COMPLETED':
        return <CheckCircle size={24} className="text-green-500" />;
      case 'FAILED':
        return <AlertTriangle size={24} className="text-red-500" />;
      default:
        return <Video size={24} className="text-purple-500" />;
    }
  };

  const { show, ToastContainer } = useToast();

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-banana-50/30 to-blue-50/50 relative overflow-hidden">
      {/* 背景装饰元素 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-green-400/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* 导航栏 */}
      <nav className="relative h-16 md:h-18 bg-white/40 backdrop-blur-2xl">
        <div className="max-w-7xl mx-auto px-4 md:px-6 h-full flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center">
              <img
                src="/logo.png"
                alt="有机系统"
                className="h-10 md:h-12 w-auto rounded-lg object-contain"
              />
            </div>
            <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-banana-600 via-green-500 to-teal-500 bg-clip-text text-transparent">
              有机系统
            </span>
          </div>
        </div>
      </nav>

      {/* 主内容 */}
      <main className="relative max-w-4xl mx-auto px-4 py-8">
        {/* 标题区 */}
        <div className="text-center mb-8 space-y-2">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 flex items-center justify-center gap-2">
            <Video size={28} className="text-purple-600" />
            视频内容分析
          </h1>
          <p className="text-gray-600">上传视频文件，AI将自动分析视频内容</p>
        </div>

        {/* 视频上传卡片 */}
        <Card className="p-6 bg-white/90 backdrop-blur-xl shadow-xl border-0 mb-8">
          <div className="space-y-6">
            {/* 文件选择区域 */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-400 transition-colors">
              {!selectedFile ? (
                <div className="space-y-4">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-100">
                    <Upload size={32} className="text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">选择视频文件</h3>
                    <p className="text-sm text-gray-600 mt-1">支持 MP4、MOV、AVI 等格式，最大 200MB</p>
                  </div>
                  <div>
                    <input
                      id="video-upload"
                      type="file"
                      accept="video/*"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <Button 
                      size="lg" 
                      onClick={() => {
                        const fileInput = document.getElementById('video-upload') as HTMLInputElement;
                        if (fileInput) {
                          fileInput.click();
                        }
                      }}
                    >
                      <Upload size={18} className="mr-2" />
                      上传视频
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-100">
                    <Video size={32} className="text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center justify-center gap-2">
                      <Play size={18} className="text-green-500" />
                      {selectedFile.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <div>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={handleRemoveFile}
                      className="text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <X size={16} className="mr-1" />
                      移除文件
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* 分析提示输入 */}
            <div>
              <label htmlFor="analysis-prompt" className="block text-sm font-medium text-gray-700 mb-2">
                分析要求
              </label>
              <Textarea
                id="analysis-prompt"
                placeholder="请输入您的分析要求，例如：分析视频的主题、内容结构、人物关系等"
                value={analysisPrompt}
                onChange={(e) => setAnalysisPrompt(e.target.value)}
                rows={3}
                className="border-2 border-gray-200 focus:border-purple-400 transition-colors"
              />
            </div>

            {/* 分析按钮 */}
            <div className="flex justify-center">
              <Button
                size="lg"
                onClick={handleAnalyze}
                disabled={!selectedFile || isAnalyzing}
                loading={isAnalyzing}
              >
                <Video size={18} className="mr-2" />
                开始分析视频
              </Button>
            </div>
          </div>
        </Card>

        {/* 状态和结果卡片 */}
        {(status.status !== 'UPLOADING' || analysisResult) && (
          <Card className="p-6 bg-white/90 backdrop-blur-xl shadow-xl border-0">
            {/* 状态显示 */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full">
                  {getStatusIcon()}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">分析状态</h3>
                  <p className="text-sm text-gray-600">{status.message}</p>
                </div>
              </div>
              {status.progress !== undefined && (
                <div className="text-sm font-medium text-purple-600">{status.progress}%</div>
              )}
            </div>

            {/* 进度条 */}
            {status.progress !== undefined && (
              <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-purple-700 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${status.progress}%` }}
                ></div>
              </div>
            )}

            {/* 加载动画 */}
            {(status.status === 'PROCESSING' || isAnalyzing) && (
              <div className="flex flex-col items-center justify-center py-8">
                <Loading message="视频正在分析中，请稍候..." />
                <p className="text-sm text-gray-500 mt-4">
                  视频分析可能需要几分钟时间，具体取决于视频长度和内容复杂度
                </p>
              </div>
            )}

            {/* 失败状态 */}
            {status.status === 'FAILED' && (
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                <AlertTriangle size={20} className="text-red-600 flex-shrink-0" />
                <p className="text-sm text-red-800">{status.message}</p>
              </div>
            )}

            {/* 分析结果 */}
            {analysisResult && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">分析结果</h3>
                <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
                  <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{analysisResult}</p>
                </div>
              </div>
            )}
          </Card>
        )}
      </main>
      <ToastContainer />
    </div>
  );
};
