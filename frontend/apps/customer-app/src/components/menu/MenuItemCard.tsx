import React from 'react';
import { Plus, Leaf, Flame, Award } from 'lucide-react';
import type { MenuItem } from '../../types/index.js';
import { formatPrice } from '../../lib/utils';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { useCartStore } from '../../store/cartStore';

interface MenuItemCardProps {
  item: MenuItem;
  onAddToCart?: (item: MenuItem) => void;
}

export const MenuItemCard: React.FC<MenuItemCardProps> = ({ item, onAddToCart }) => {
  const { addItem, getItem } = useCartStore();
  const cartItem = getItem(item.id);

  const handleAddToCart = () => {
    addItem(item);
    onAddToCart?.(item);
  };

  const getDietaryIcon = (tag: string) => {
    const lowerTag = tag.toLowerCase();
    if (lowerTag.includes('vegan') || lowerTag.includes('vegetarian')) {
      return <Leaf className="w-3 h-3" />;
    }
    if (lowerTag.includes('spicy')) {
      return <Flame className="w-3 h-3" />;
    }
    return null;
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm hover:shadow-md transition-all overflow-hidden border border-border">
      {/* Image */}
      {item.image && (
        <div className="relative aspect-video overflow-hidden">
          <img
            src={item.image}
            alt={item.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
          {item.is_special_of_day && (
            <div className="absolute top-3 left-3">
              <Badge variant="warning" className="gap-1">
                <Award className="w-3 h-3" />
                Special
              </Badge>
            </div>
          )}
          {!item.is_available && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <span className="text-white font-semibold text-lg">Unavailable</span>
            </div>
          )}
        </div>
      )}

      {/* Content */}
      <div className="p-4">
        {/* Header */}
        <div className="flex justify-between items-start mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-foreground text-lg leading-tight">
              {item.name}
            </h3>
            {item.dietary_tags && item.dietary_tags.length > 0 && (
              <div className="flex gap-1 mt-1.5">
                {item.dietary_tags.slice(0, 3).map((tag, index) => (
                  <Badge key={index} variant="info" className="text-xs gap-1">
                    {getDietaryIcon(tag)}
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
          </div>
          <div className="text-right ml-3">
            <p className="text-xl font-bold text-primary">
              {formatPrice(item.price)}
            </p>
          </div>
        </div>

        {/* Description */}
        {item.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {item.description}
          </p>
        )}

        {/* Allergens */}
        {item.allergens && item.allergens.length > 0 && (
          <div className="mb-3">
            <p className="text-xs text-muted-foreground">
              Allergens: {item.allergens.join(', ')}
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between gap-3">
          <div className="text-xs text-muted-foreground">
            <span>{item.preparation_time} min</span>
          </div>

          <Button
            size="sm"
            onClick={handleAddToCart}
            disabled={!item.is_available}
            icon={<Plus className="w-4 h-4" />}
          >
            {cartItem ? `In Cart (${cartItem.quantity})` : 'Add'}
          </Button>
        </div>
      </div>
    </div>
  );
};
