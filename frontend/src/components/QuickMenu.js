import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ChevronDown, ChevronUp, Sparkles } from 'lucide-react';

const MenuContainer = styled.div`
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
`;

const MenuHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #21262d;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #30363d;
  }
`;

const MenuTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #c9d1d9;
`;

const MenuContent = styled.div`
  max-height: ${props => props.isOpen ? '400px' : '0'};
  overflow: hidden;
  transition: max-height 0.3s ease;
`;

const MenuGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  padding: 16px;
`;

const MenuItem = styled.div`
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #30363d;
    border-color: #58a6ff;
    transform: translateY(-1px);
  }
`;

const MenuItemTitle = styled.div`
  font-weight: 600;
  color: #c9d1d9;
  margin-bottom: 4px;
  font-size: 14px;
`;

const MenuItemDescription = styled.div`
  color: #8b949e;
  font-size: 12px;
  line-height: 1.4;
`;

const QuickMenu = ({ onQuerySelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMenuItems();
  }, []);

  const fetchMenuItems = async () => {
    setLoading(true);
    try {
      // Since the backend doesn't have a quick-menu endpoint, we'll use fallback items
      console.log('📋 QuickMenu: Using fallback menu items');
      setMenuItems([
        {
          id: 'overview',
          title: '📊 Data Overview',
          description: 'Get a summary of your dataset',
          query: 'Show me an overview of the data'
        },
        {
          id: 'statistics',
          title: '📈 Statistical Analysis',
          description: 'View descriptive statistics',
          query: 'What are the mean and average values?'
        },
        {
          id: 'trends',
          title: '📉 Trend Analysis',
          description: 'Identify patterns over time',
          query: 'Show me the trends in the data'
        },
        {
          id: 'correlations',
          title: '🔗 Correlation Analysis',
          description: 'Find relationships between variables',
          query: 'What correlations exist in the data?'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleMenuItemClick = (query) => {
    onQuerySelect(query);
    setIsOpen(false);
  };

  return (
    <MenuContainer>
      <MenuHeader onClick={() => setIsOpen(!isOpen)}>
        <MenuTitle>
          <Sparkles size={16} color="#58a6ff" />
          Quick Analysis Menu
        </MenuTitle>
        {isOpen ? <ChevronUp size={16} color="#8b949e" /> : <ChevronDown size={16} color="#8b949e" />}
      </MenuHeader>
      
      <MenuContent isOpen={isOpen}>
        <MenuGrid>
          {menuItems.map((item) => (
            <MenuItem 
              key={item.id} 
              onClick={() => handleMenuItemClick(item.query)}
            >
              <MenuItemTitle>{item.title}</MenuItemTitle>
              <MenuItemDescription>{item.description}</MenuItemDescription>
            </MenuItem>
          ))}
        </MenuGrid>
      </MenuContent>
    </MenuContainer>
  );
};

export default QuickMenu; 