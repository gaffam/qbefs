import { Layout, Row, Col } from 'antd';
import EquityCurveChart from './components/EquityCurveChart';
import KpiCards from './components/KpiCards';
import './App.css';

const { Header, Content, Footer } = Layout;

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ color: 'white', fontSize: '20px' }}>
        Icerberg Terminali v1.0
      </Header>
      <Content style={{ padding: '24px 50px' }}>
        <div className="site-layout-content" style={{ background: '#fff', padding: 24 }}>
          <KpiCards />
          <Row gutter={16}>
            <Col span={24}>
              <EquityCurveChart />
            </Col>
            {/* Diğer bileşenler için yerler */}
          </Row>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Icerberg Terminali ©{new Date().getFullYear()} - Halk İçin, Halka Rağmen.
      </Footer>
    </Layout>
  );
}

export default App;
