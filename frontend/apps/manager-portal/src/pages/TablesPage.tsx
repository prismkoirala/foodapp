import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { managerApi } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { QrCode, Eye, Download, Plus, Save, X, Trash2 } from 'lucide-react';
import Button from '../components/ui/Button';

interface Table {
  id: number;
  table_number: string;
  qr_code: string;
  qr_code_image: string | null;
  is_active: boolean;
  capacity: number;
}

export default function TablesPage() {
  const queryClient = useQueryClient();
  const [isCreating, setIsCreating] = useState(false);
  const [tableForm, setTableForm] = useState({
    table_number: '',
    capacity: 4,
    is_active: true,
  });

  const { data: tables = [], isLoading } = useQuery<Table[]>({
    queryKey: ['manager-tables'],
    queryFn: () => managerApi.getTables().then(res => res.data.results || res.data),
    refetchInterval: 10000,
  });

  // Create table mutation
  const createTableMutation = useMutation({
    mutationFn: (data: any) => managerApi.createTable(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-tables'] });
      setIsCreating(false);
      setTableForm({ table_number: '', capacity: 4, is_active: true });
      alert('Table created successfully with QR code!');
    },
    onError: (error: any) => {
      alert(`Failed to create table: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Delete table mutation
  const deleteTableMutation = useMutation({
    mutationFn: (tableId: number) => managerApi.deleteTable(tableId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['manager-tables'] });
      alert('Table and QR code deleted successfully!');
    },
    onError: (error: any) => {
      alert(`Failed to delete table: ${error.response?.data?.detail || error.message}`);
    },
  });

  const handleCreateStart = () => {
    setIsCreating(true);
  };

  const handleCreateSave = () => {
    if (!tableForm.table_number) {
      alert('Please enter a table number');
      return;
    }
    createTableMutation.mutate(tableForm);
  };

  const handleCreateCancel = () => {
    setIsCreating(false);
    setTableForm({ table_number: '', capacity: 4, is_active: true });
  };

  const getQRCodeUrl = (qrCode: string) => {
    return `${window.location.origin}/qr/${qrCode}`;
  };

  const handleViewQR = (qrCodeImage: string | null, tableNumber: string) => {
    if (qrCodeImage) {
      window.open(qrCodeImage, '_blank');
    } else {
      alert('QR code image not available');
    }
  };

  const handleDownloadQR = async (qrCodeImage: string | null, tableNumber: string) => {
    if (!qrCodeImage) {
      alert('QR code image not available');
      return;
    }

    try {
      // Fetch the image as a blob to avoid CORS issues
      const response = await fetch(qrCodeImage);
      const blob = await response.blob();

      // Create object URL and download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${tableNumber.replace(/\s+/g, '_')}_QR.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading QR code:', error);
      alert('Failed to download QR code');
    }
  };

  const handleDeleteTable = (tableId: number, tableNumber: string) => {
    if (confirm(`Are you sure you want to delete "${tableNumber}" and its QR code?\n\nThis action cannot be undone.`)) {
      deleteTableMutation.mutate(tableId);
    }
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tables & QR Codes</h1>
          <p className="text-gray-600 mt-2">
            Manage your restaurant tables and QR codes for customer ordering
          </p>
        </div>
        <Button
          onClick={handleCreateStart}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Table
        </Button>
      </div>

      {/* Create Table Form */}
      {isCreating && (
        <Card className="mb-6 border-2 border-blue-500 shadow-lg">
          <CardHeader>
            <CardTitle className="text-lg">Create New Table</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Table Number *
                </label>
                <input
                  type="text"
                  value={tableForm.table_number}
                  onChange={(e) => setTableForm({ ...tableForm, table_number: e.target.value })}
                  placeholder="e.g. Table 1, Patio 3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Capacity
                </label>
                <input
                  type="number"
                  value={tableForm.capacity}
                  onChange={(e) => setTableForm({ ...tableForm, capacity: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={tableForm.is_active}
                onChange={(e) => setTableForm({ ...tableForm, is_active: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                Active (customers can order from this table)
              </label>
            </div>
            <div className="flex gap-2 pt-2">
              <Button
                onClick={handleCreateSave}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
                isLoading={createTableMutation.isPending}
              >
                <Save className="w-4 h-4 mr-2" />
                Create Table & Generate QR
              </Button>
              <Button
                onClick={handleCreateCancel}
                variant="secondary"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {tables.length === 0 && !isCreating && (
        <Card>
          <CardContent className="p-12 text-center">
            <QrCode className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Tables Yet</h3>
            <p className="text-gray-600 mb-6">Create tables with QR codes for customer ordering</p>
            <Button
              onClick={handleCreateStart}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create First Table
            </Button>
          </CardContent>
        </Card>
      )}

      {tables.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tables.map((table) => (
            <Card key={table.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="bg-gradient-to-br from-blue-50 to-indigo-50">
                <CardTitle className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-gray-900">
                    {table.table_number}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    table.is_active
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {table.is_active ? 'Active' : 'Inactive'}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                {/* QR Code */}
                <div className="bg-gray-50 rounded-lg p-4 mb-4 text-center">
                  {table.qr_code_image ? (
                    <img
                      src={table.qr_code_image}
                      alt={`QR Code for ${table.table_number}`}
                      className="w-32 h-32 mx-auto"
                    />
                  ) : (
                    <QrCode className="w-32 h-32 text-gray-300 mx-auto" />
                  )}
                  <p className="text-xs text-gray-500 mt-2 font-mono break-all">
                    {table.qr_code.substring(0, 20)}...
                  </p>
                </div>

                {/* Table Info */}
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Capacity:</span>
                    <span className="font-semibold text-gray-900">{table.capacity} people</span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-600">Customer URL:</span>
                    <p className="font-mono text-xs text-blue-600 mt-1 break-all">
                      {getQRCodeUrl(table.qr_code)}
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="space-y-2">
                  <div className="grid grid-cols-2 gap-2">
                    <Button
                      onClick={() => handleViewQR(table.qr_code_image, table.table_number)}
                      variant="secondary"
                      size="sm"
                      className="w-full"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    <Button
                      onClick={() => handleDownloadQR(table.qr_code_image, table.table_number)}
                      variant="secondary"
                      size="sm"
                      className="w-full"
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Download
                    </Button>
                  </div>
                  <Button
                    onClick={() => handleDeleteTable(table.id, table.table_number)}
                    variant="secondary"
                    size="sm"
                    className="w-full bg-red-50 text-red-700 hover:bg-red-100 border-red-200"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Delete Table
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
