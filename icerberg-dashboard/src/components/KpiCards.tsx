import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, Statistic, Row, Col, Spin, Alert } from 'antd';

interface KpiData {
  cagr: number;
  sharpe: number;
  max_drawdown: number;
  position_count: number;
}

const KpiCards = () => {
  const [data, setData] = useState<KpiData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await axios.get('http://localhost:8000/api/kpis');
        setData(res.data);
        setError(null);
      } catch (err) {
        setError('KPI verileri alınamadı.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Spin tip="KPI verileri yükleniyor..." />;
  if (error) return <Alert message="Hata" description={error} type="error" showIcon />;
  if (!data) return null;

  return (
    <Row gutter={16} style={{ marginBottom: 24 }}>
      <Col span={6}><Card><Statistic title="CAGR" value={data.cagr} suffix="%" precision={2} /></Card></Col>
      <Col span={6}><Card><Statistic title="Sharpe" value={data.sharpe} precision={2} /></Card></Col>
      <Col span={6}><Card><Statistic title="Max Drawdown" value={data.max_drawdown} suffix="%" precision={2} /></Card></Col>
      <Col span={6}><Card><Statistic title="Pozisyon Sayısı" value={data.position_count} /></Card></Col>
    </Row>
  );
};

export default KpiCards;
