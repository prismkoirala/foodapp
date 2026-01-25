import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { QrCode } from 'lucide-react';
import { customerApi } from '../lib/api';

export const QRLandingPage: React.FC = () => {
  const { qrCode } = useParams<{ qrCode: string }>();
  const navigate = useNavigate();

  const { data: qrData, isLoading, isError } = useQuery({
    queryKey: ['qr-resolve', qrCode],
    queryFn: () => customerApi.resolveQR(qrCode!).then(res => res.data),
    enabled: !!qrCode,
    retry: 1,
  });

  useEffect(() => {
    if (qrData) {
      // Redirect to menu page with restaurant ID and table parameter
      const url = `/menu/${qrData.restaurant_id}${qrData.table_id ? `?table=${qrData.table_id}` : ''}`;
      navigate(url, { replace: true });
    }
  }, [qrData, navigate]);

  if (isError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center max-w-md px-4">
          <div className="text-red-500 mb-4">
            <QrCode className="w-16 h-16 mx-auto" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-4">Invalid QR Code</h2>
          <p className="text-muted-foreground mb-6">
            The QR code you scanned is invalid or has expired. Please try scanning again or contact
            the restaurant staff for assistance.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="mb-6">
          <QrCode className="w-16 h-16 text-primary mx-auto animate-pulse" />
        </div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Loading Menu...</h2>
        <p className="text-muted-foreground">
          {isLoading ? 'Resolving QR code...' : 'Redirecting to menu...'}
        </p>
        <div className="mt-6">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto"></div>
        </div>
      </div>
    </div>
  );
};
