openerp.tt_print_forms_names = function(instance) {
    var module = instance.web;
    var QWeb = instance.web.qweb;

module.ActionManager = module.ActionManager.extend({
    ir_actions_report_xml: function(action, options) {
        var self = this;
        instance.web.blockUI();
        return instance.web.pyeval.eval_domains_and_contexts({
            contexts: [action.context],
            domains: []
        }).then(function(res) {
            action = _.clone(action);
            action.context = res.context;

            // iOS devices doesn't allow iframe use the way we do it,
            // opening a new window seems the best way to workaround
            if (navigator.userAgent.match(/(iPod|iPhone|iPad)/)) {
                var params = {
                    action: JSON.stringify(action),
                    token: new Date().getTime()
                }
                var url = self.session.url('/web/named_report', params)
                instance.web.unblockUI();
                $('<a href="'+url+'" target="_blank"></a>')[0].click();
                return;
            }

            var c = instance.webclient.crashmanager;
            return $.Deferred(function (d) {
                self.session.get_file({
                    url: '/web/named_report',
                    data: {action: JSON.stringify(action)},
                    complete: instance.web.unblockUI,
                    success: function(){
                        if (!self.dialog) {
                            options.on_close();
                        }
                        self.dialog_stop();
                        d.resolve();
                    },
                    error: function () {
                        c.rpc_error.apply(c, arguments);
                        d.reject();
                    }
                })
            });
        });
    }
});


module.ViewManagerAction = module.ViewManagerAction.extend({
    on_debug_changed: function (evt) {
        var self = this,
            $sel = $(evt.currentTarget),
            $option = $sel.find('option:selected'),
            val = $sel.val(),
            current_view = this.views[this.active_view].controller;
        switch (val) {
            case 'fvg':
                var dialog = new instance.web.Dialog(this, { title: _t("Fields View Get"), width: '95%' }).open();
                $('<pre>').text(instance.web.json_node_to_xml(current_view.fields_view.arch, true)).appendTo(dialog.$el);
                break;
            case 'tests':
                this.do_action({
                    name: _t("JS Tests"),
                    target: 'new',
                    type : 'ir.actions.act_url',
                    url: '/web/tests?mod=*'
                });
                break;
            case 'perm_read':
                var ids = current_view.get_selected_ids();
                if (ids.length === 1) {
                    this.dataset.call('perm_read', [ids]).done(function(result) {
                        var dialog = new instance.web.Dialog(this, {
                            title: _.str.sprintf(_t("View Log (%s)"), self.dataset.model),
                            width: 400
                        }, QWeb.render('ViewManagerDebugViewLog', {
                            perm : result[0],
                            format : instance.web.format_value
                        })).open();
                    });
                }
                break;
            case 'toggle_layout_outline':
                current_view.rendering_engine.toggle_layout_debugging();
                break;
            case 'set_defaults':
                current_view.open_defaults_dialog();
                break;
            case 'translate':
                this.do_action({
                    name: _t("Technical Translation"),
                    res_model : 'ir.translation',
                    domain : [['type', '!=', 'object'], '|', ['name', '=', this.dataset.model], ['name', 'ilike', this.dataset.model + ',']],
                    views: [[false, 'list'], [false, 'form']],
                    type : 'ir.actions.act_window',
                    view_type : "list",
                    view_mode : "list"
                });
                break;
            case 'fields':
                this.dataset.call('fields_get', [false, {}]).done(function (fields) {
                    var $root = $('<dl>');
                    _(fields).each(function (attributes, name) {
                        $root.append($('<dt>').append($('<h4>').text(name)));
                        var $attrs = $('<dl>').appendTo($('<dd>').appendTo($root));
                        _(attributes).each(function (def, name) {
                            if (def instanceof Object) {
                                def = JSON.stringify(def);
                            }
                            $attrs
                                .append($('<dt>').text(name))
                                .append($('<dd style="white-space: pre-wrap;">').text(def));
                        });
                    });
                    new instance.web.Dialog(self, {
                        title: _.str.sprintf(_t("Model %s fields"),
                                             self.dataset.model),
                        width: '95%'}, $root).open();
                });
                break;
            case 'edit_workflow':
                return this.do_action({
                    res_model : 'workflow',
                    domain : [['osv', '=', this.dataset.model]],
                    views: [[false, 'list'], [false, 'form'], [false, 'diagram']],
                    type : 'ir.actions.act_window',
                    view_type : 'list',
                    view_mode : 'list'
                });
                break;
            case 'edit':
                this.do_edit_resource($option.data('model'), $option.data('id'), { name : $option.text() });
                break;
            case 'manage_filters':
                this.do_action({
                    res_model: 'ir.filters',
                    views: [[false, 'list'], [false, 'form']],
                    type: 'ir.actions.act_window',
                    context: {
                        search_default_my_filters: true,
                        search_default_model_id: this.dataset.model
                    }
                });
                break;
            case 'print_workflow':
                if (current_view.get_selected_ids  && current_view.get_selected_ids().length == 1) {
                    instance.web.blockUI();
                    var action = {
                        context: { active_ids: current_view.get_selected_ids() },
                        report_name: "workflow.instance.graph",
                        datas: {
                            model: this.dataset.model,
                            id: current_view.get_selected_ids()[0],
                            nested: true,
                        }
                    };
                    this.session.get_file({
                        url: '/web/named_report',
                        data: {action: JSON.stringify(action)},
                        complete: instance.web.unblockUI
                    });
                }
                break;
            default:
                if (val) {
                    console.log("No debug handler for ", val);
                }
        }
        evt.currentTarget.selectedIndex = 0;
    }
});


};