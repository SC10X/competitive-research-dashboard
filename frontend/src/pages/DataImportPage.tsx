import { useState, useCallback, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Upload,
  FileSpreadsheet,
  FileText,
  CheckCircle,
  XCircle,
  Download,
  Trash2,
  Clock,
} from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { EmptyState } from '@/components/ui/EmptyState'
import { DataTable } from '@/components/ui/DataTable'
import type { Column } from '@/components/ui/DataTable'

interface ImportFile {
  id: string
  name: string
  size: number
  type: string
  file: File
}

interface ImportHistoryItem {
  id: number
  fileName: string
  importType: string
  status: 'success' | 'failed' | 'processing'
  recordCount: number
  createdAt: string
  errorMessage?: string
}

const mockHistory: ImportHistoryItem[] = [
  {
    id: 1,
    fileName: 'brands_2024_q1.xlsx',
    importType: '品牌数据',
    status: 'success',
    recordCount: 150,
    createdAt: '2024-03-15 14:30',
  },
  {
    id: 2,
    fileName: 'social_media_data.csv',
    importType: '社媒数据',
    status: 'success',
    recordCount: 320,
    createdAt: '2024-03-10 09:15',
  },
  {
    id: 3,
    fileName: 'pricing_update.xlsx',
    importType: '价格数据',
    status: 'failed',
    recordCount: 0,
    createdAt: '2024-03-08 16:45',
    errorMessage: '文件格式错误：缺少必填列 "brand_name"',
  },
]

const importTypeOptions = [
  { value: 'brand', label: '品牌数据' },
  { value: 'pricing', label: '价格数据' },
  { value: 'social', label: '社媒数据' },
  { value: 'financial', label: '财务数据' },
]

export default function DataImportPage() {
  const [files, setFiles] = useState<ImportFile[]>([])
  const [importType, setImportType] = useState('brand')
  const [previewData, setPreviewData] = useState<Record<string, unknown>[] | null>(null)
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<{ success: boolean; message: string } | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substring(7),
      name: file.name,
      size: file.size,
      type: file.name.endsWith('.csv') ? 'csv' : 'excel',
      file,
    }))
    setFiles((prev) => [...prev, ...newFiles])
    setImportResult(null)

    // Simulate preview for the first file
    if (acceptedFiles.length > 0) {
      setPreviewData([
        { brand_name: 'Nike', country: 'US', price_tier: 'premium', founded_year: 1964 },
        { brand_name: 'Adidas', country: 'DE', price_tier: 'premium', founded_year: 1949 },
        { brand_name: 'H&M', country: 'SE', price_tier: 'budget', founded_year: 1947 },
      ])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxSize: 10 * 1024 * 1024,
  })

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
    if (files.length <= 1) {
      setPreviewData(null)
    }
  }

  const handleImport = async () => {
    setImporting(true)
    setImportResult(null)
    // Simulate import process
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setImporting(false)
    setImportResult({
      success: true,
      message: `成功导入 ${previewData?.length || 0} 条${importTypeOptions.find((o) => o.value === importType)?.label}记录`,
    })
    setFiles([])
    setPreviewData(null)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const previewColumns: Column<Record<string, unknown>>[] = previewData
    ? Object.keys(previewData[0] || {}).map((key) => ({
        key,
        title: key,
        sortable: true,
      }))
    : []

  const historyColumns: Column<ImportHistoryItem>[] = [
    { key: 'fileName', title: '文件名', sortable: true },
    {
      key: 'importType',
      title: '导入类型',
      render: (value: unknown) => (
        <Badge variant="primary" size="sm">{String(value)}</Badge>
      ),
    },
    {
      key: 'status',
      title: '状态',
      render: (value: unknown) => {
        const status = String(value)
        if (status === 'success') {
          return (
            <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
              <CheckCircle className="h-4 w-4" />
              成功
            </span>
          )
        }
        if (status === 'failed') {
          return (
            <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
              <XCircle className="h-4 w-4" />
              失败
            </span>
          )
        }
        return (
          <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
            <Clock className="h-4 w-4" />
            处理中
          </span>
        )
      },
    },
    { key: 'recordCount', title: '记录数', sortable: true },
    { key: 'createdAt', title: '导入时间', sortable: true },
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white">数据导入</h1>
        <p className="mt-1 text-surface-500 dark:text-surface-400">
          上传 Excel/CSV 文件导入品牌数据
        </p>
      </div>

      {/* Upload Area */}
      <Card>
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
          上传文件
        </h2>

        {/* Import Type Selector */}
        <div className="mb-4">
          <label className="text-sm font-medium text-surface-500 dark:text-surface-400 mb-2 block">
            导入类型
          </label>
          <div className="flex flex-wrap gap-2">
            {importTypeOptions.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setImportType(opt.value)}
                className={`px-4 py-2 text-sm rounded-lg border transition-colors ${
                  importType === opt.value
                    ? 'border-primary-300 bg-primary-50 text-primary-700 dark:border-primary-700 dark:bg-primary-900/30 dark:text-primary-300'
                    : 'border-surface-200 text-surface-500 hover:bg-surface-50 dark:border-surface-700 dark:text-surface-400 dark:hover:bg-surface-800'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
            isDragActive
              ? 'border-primary-400 bg-primary-50 dark:border-primary-600 dark:bg-primary-900/20'
              : 'border-surface-300 dark:border-surface-600 hover:border-primary-300 dark:hover:border-primary-700'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-10 w-10 mx-auto text-surface-400 mb-3" />
          {isDragActive ? (
            <p className="text-primary-600 dark:text-primary-400 font-medium">
              拖放文件到此处...
            </p>
          ) : (
            <>
              <p className="text-surface-600 dark:text-surface-400 font-medium">
                拖放文件到此处，或点击选择文件
              </p>
              <p className="text-sm text-surface-400 mt-1">
                支持 .xlsx, .xls, .csv 格式，最大 10MB
              </p>
            </>
          )}
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="mt-4 space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between px-4 py-3 rounded-lg bg-surface-50 dark:bg-surface-800"
              >
                <div className="flex items-center gap-3">
                  {file.type === 'csv' ? (
                    <FileText className="h-5 w-5 text-surface-400" />
                  ) : (
                    <FileSpreadsheet className="h-5 w-5 text-green-600 dark:text-green-400" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-surface-900 dark:text-white">
                      {file.name}
                    </p>
                    <p className="text-xs text-surface-400">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(file.id)}
                  className="p-1.5 rounded-lg text-surface-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Preview */}
      {previewData && previewData.length > 0 && (
        <Card>
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
            数据预览
          </h2>
          <DataTable columns={previewColumns} data={previewData} pageSize={5} />
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-surface-400">
              共 {previewData.length} 条预览记录
            </p>
            <Button
              onClick={handleImport}
              loading={importing}
              disabled={files.length === 0}
            >
              <Download className="h-4 w-4" />
              {importing ? '导入中...' : '执行导入'}
            </Button>
          </div>
        </Card>
      )}

      {/* Import Result */}
      {importResult && (
        <Card
          className={
            importResult.success
              ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
              : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
          }
        >
          <div className="flex items-center gap-3">
            {importResult.success ? (
              <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
            ) : (
              <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
            )}
            <div>
              <p className="font-medium text-surface-900 dark:text-white">
                {importResult.success ? '导入成功' : '导入失败'}
              </p>
              <p className="text-sm text-surface-600 dark:text-surface-400">
                {importResult.message}
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Import History */}
      <Card>
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
          导入历史
        </h2>
        {mockHistory.length === 0 ? (
          <EmptyState title="暂无导入记录" description="还没有进行过数据导入" />
        ) : (
          <DataTable columns={historyColumns as unknown as Column<Record<string, unknown>>[]} data={mockHistory as unknown as Record<string, unknown>[]} pageSize={10} />
        )}
      </Card>
    </div>
  )
}
