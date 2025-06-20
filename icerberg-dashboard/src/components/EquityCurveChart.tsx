import { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, Spin, Alert } from 'antd';

interface EquityDataPoint {
  date: string;
  portfolio: number;
  benchmark: number;
}

const EquityCurveChart = () => {
  const [data, setData] = useState<EquityDataPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/api/equity-curve');
        setData(response.data);
        setError(null);
      } catch (err) {
        setError('Veri çekilirken bir hata oluştu.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <Spin tip="Performans verileri yükleniyor..." size="large" />;
  }

  if (error) {
    return <Alert message="Hata" description={error} type="error" showIcon />;
  }

  return (
    <Card title="Stratejinin Kalp Atışı (Performans Grafiği)">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis tickFormatter={(t) => `${(t / 1000).toFixed(0)}k`} />
          <Tooltip formatter={(v: number) => v.toLocaleString('tr-TR', { style: 'currency', currency: 'TRY' })} />
          <Legend />
          <Line type="monotone" dataKey="portfolio" name="Icerberg Portföyü" stroke="#8884d8" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="benchmark" name="XU100 Benchmark" stroke="#82ca9d" strokeWidth={1} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default EquityCurveChart;
