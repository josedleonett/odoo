from odoo import models, fields, api

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    
    total_operation_time = fields.Float(
        string='Total operations time',
        compute='_compute_total_operation_time',
        help=(
            'Suma de los tiempos de ciclo manual de las operaciones de esta BoM y sus componentes hijos. '
            'El tiempo se calcula en minutos y segundos.'
        ),
        store=True
    )
    
    @api.depends(
        'operation_ids.time_cycle_manual', 
        'bom_line_ids.product_id.bom_ids.total_operation_time',
        'bom_line_ids.product_id.bom_ids.bom_line_ids.product_id.bom_ids.total_operation_time'
    )
    def _compute_total_operation_time(self):
        for record in self:
            # Inicializar el tiempo total con las operaciones directas
            total_time = sum(record.operation_ids.mapped('time_cycle_manual'))
            
            # Agregar tiempos de las BoMs hijas de manera recursiva
            for bom_line in record.bom_line_ids:
                for child_bom in bom_line.product_id.bom_ids:
                    total_time += child_bom.total_operation_time
            
            record.total_operation_time = total_time
    
    def action_recompute_total_operation_time(self):
        """Método para forzar la actualización recursiva de tiempos de operación"""
        def recursive_update(boms):
            # Recalcular para este conjunto de BoMs
            boms._compute_total_operation_time()
            
            # Buscar y actualizar BoMs hijas
            child_boms = boms.mapped('bom_line_ids.product_id.bom_ids')
            if child_boms:
                recursive_update(child_boms)
        
        # Iniciar actualización recursiva desde los registros actuales
        recursive_update(self)
        
        return True