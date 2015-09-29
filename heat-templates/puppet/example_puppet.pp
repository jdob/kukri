file { '/tmp/puppet_managed': ensure => present }

file { 'hiera_contents_example':
    ensure => file,
    mode => '0644',
    path => '/tmp/hiera_contents',
    content => hiera('example_heat_key'),
}
